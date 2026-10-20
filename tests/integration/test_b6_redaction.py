"""REQ-B6-091 — governed expurgation of vehicle identifiers from
vir_resolution artifacts. Fictitious plate and VIN only."""
import io
import json
import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from app.cpl.identity.authority import AuthorityContext
from app.cpl.models.asset import Asset
from app.cpl.models.case import Case
from app.cpl.models.contact import Contact
from app.cpl.models.runner_artifact import RunnerArtifact
from app.cpl.models.runner_artifact_redaction import RunnerArtifactRedaction
from app.cpl.models.runner_artifact_schema_definition import RunnerArtifactSchemaDefinition
from app.cpl.models.runner_governance_decision import RunnerGovernanceDecision
from app.cpl.runners import redaction as r
from app.cpl.runners.artifacts import (
    check_supersession_consistency, compute_content_hash, register_artifact, supersede_artifact,
)
from app.cpl.runners.authority import RunnerAuthority
from app.cpl.runners.execution import admit_execution
from app.cpl.runners.outcomes import RunnerOutcome
from app.cpl.runners.redaction_command import run as run_command
from app.db.engine import check_db_connection

VIN = "VF3FICTIF0E2E0042"
PLATE = "ZZ-042-ZZ"
OTHER_VIN = "VF3FICTIF0E2E0099"


def vir_payload(resolution_id="VIR-RES-FICTIF-1"):
    """A vir_resolution payload holding the identifiers in every location of
    VIR's schema, as VehicleIdentityResolution.model_dump(mode="json") lays it out."""
    def identity(vin, plate):
        return {"manufacturer": "Peugeot", "model": "3008", "generation": "II",
                "engine": {"power_kw": 96.0}, "production": {"year": 2019},
                "identifiers": {"vin": vin, "registration_number": plate, "registration_country": "FR"}}

    def evidence(path, value):
        return {"field_path": path, "resolved_value": value, "confidence": "high",
                "sources": [{"source_id": "provider-fr-regcheck", "reported_value": value, "source_value": value,
                             "reliability": "high", "method": "registry_lookup", "provider_field": None}],
                "consulted_without_value": [{"source_id": "provider-vincario-vin", "reported_value": value,
                                             "reliability": "medium"}]}

    return {
        "request_id": "PI-REQ-OPAQUE-1", "resolution_id": resolution_id, "resolution_status": "resolved",
        "confidence": {"score": 0.9, "level": "high"},
        "vehicle_identity": identity(VIN, PLATE),
        "alternative_candidates": [{"candidate_id": "C2", "identity": identity(OTHER_VIN, PLATE),
                                    "field_evidence": [evidence("identifiers.vin", OTHER_VIN),
                                                       evidence("engine.power_kw", 96.0)]}],
        "excluded_candidates": [{"candidate": {"candidate_id": "C3", "identity": identity(OTHER_VIN, None),
                                               "field_evidence": [evidence("identifiers.registration_number", PLATE)]},
                                 "field_provenance": [{"field_path": "identifiers.vin", "source_id": "provider-vincario-vin",
                                                       "raw_value": OTHER_VIN},
                                                      {"field_path": "engine.power_kw", "source_id": "provider-vincario-vin",
                                                       "raw_value": 110}],
                                 "reason": "declared_value_mismatch", "field_path": "identifiers.vin",
                                 "declared_value": VIN, "candidate_value": OTHER_VIN}],
        "provider_unconfirmed_fields": [
            {"source_id": "provider-fr-regcheck", "provider_field": "numSerieMoteur", "raw_value": VIN,
             "kind": "to_confirm", "note": "correspondance à confirmer par le propriétaire"},
            {"source_id": "provider-fr-regcheck", "provider_field": "anneeSortie", "raw_value": "2019",
             "kind": "to_confirm", "note": "correspondance à confirmer par le propriétaire"}],
        "provider_descriptive_info": [{"source_id": "provider-fr-regcheck", "provider_field": "CNIT",
                                       "label": "CNIT", "value": "M10PGTVP000A123"}],
        "unresolved_fields": ["generation"],
        "contradictions": [{"contradiction_id": "K1", "field_path": "identifiers.vin", "severity": "high",
                            "values": [{"value": VIN, "source_id": "a"}, {"value": OTHER_VIN, "source_id": "b"}]},
                           {"contradiction_id": "K2", "field_path": "engine.power_kw", "severity": "low",
                            "values": [{"value": 96, "source_id": "a"}, {"value": 110, "source_id": "b"}]}],
        "clarification_questions": [{"question_id": "VIR-Q-VIN", "target_field": "identifiers.vin",
                                     "reason": "vin_required_for_exact_configuration", "question_type": "single_choice",
                                     "prompt": "Pouvez-vous indiquer le VIN ?",
                                     "choices": [{"label": VIN, "value": VIN}]}],
        "field_evidence": [evidence("identifiers.vin", VIN), evidence("identifiers.registration_number", PLATE),
                           evidence("identifiers.registration_country", "FR"), evidence("model", "3008")],
        "source_summary": [{"source_id": "provider-fr-regcheck", "retrieved_at": "2026-10-20T10:00:00Z",
                            "reliability": "high", "fields_provided": ["identifiers.vin", "model"]}],
        "limitations": ["Identity is provisional pending additional verification."],
        "registration_country": "FR",
        "user_confirmed_fields": ["engine.power_kw"],
    }


def _no_identifier(obj) -> None:
    dumped = json.dumps(obj, ensure_ascii=False, default=str)
    for value in (VIN, PLATE, OTHER_VIN):
        assert value not in dumped, value


# --- 1. the locations, from the schema ---------------------------------------------------------------------------

def test_every_identifier_location_is_emptied_and_everything_else_is_kept():
    original = vir_payload()
    redacted, removed = r.redact_vehicle_identifiers(original)
    _no_identifier(redacted)
    assert original == vir_payload()                                   # the input is never changed
    assert set(redacted) == set(original)
    ident = redacted["vehicle_identity"]["identifiers"]
    assert ident == {"vin": None, "registration_number": None, "registration_country": "FR"}
    assert redacted["vehicle_identity"]["model"] == "3008" and redacted["vehicle_identity"]["engine"] == {"power_kw": 96.0}
    # Provenance kept: every evidence entry, its path, its sources and their method; only the values go.
    assert [fe["field_path"] for fe in redacted["field_evidence"]] == [fe["field_path"] for fe in original["field_evidence"]]
    vin_fe = redacted["field_evidence"][0]
    assert vin_fe["resolved_value"] is None and vin_fe["sources"][0]["source_id"] == "provider-fr-regcheck"
    assert vin_fe["sources"][0]["method"] == "registry_lookup" and vin_fe["sources"][0]["reported_value"] is None
    assert redacted["field_evidence"][2] == original["field_evidence"][2]      # registration country
    assert redacted["field_evidence"][3] == original["field_evidence"][3]
    # Contradictions kept, identifier values emptied; others untouched.
    assert [v["source_id"] for v in redacted["contradictions"][0]["values"]] == ["a", "b"]
    assert redacted["contradictions"][1] == original["contradictions"][1]
    assert redacted["alternative_candidates"][0]["field_evidence"][1] == original["alternative_candidates"][0]["field_evidence"][1]
    exc = redacted["excluded_candidates"][0]
    assert exc["field_provenance"][1] == original["excluded_candidates"][0]["field_provenance"][1]
    assert exc["reason"] == "declared_value_mismatch" and exc["declared_value"] is None
    assert redacted["provider_unconfirmed_fields"][1] == original["provider_unconfirmed_fields"][1]
    assert redacted["provider_unconfirmed_fields"][0]["provider_field"] == "numSerieMoteur"
    for key in ("resolution_id", "request_id", "provider_descriptive_info", "source_summary", "limitations",
                "unresolved_fields", "user_confirmed_fields", "registration_country", "confidence"):
        assert redacted[key] == original[key], key
    # Locations are named, never valued.
    assert "vehicle_identity.identifiers.vin" in removed and "provider_unconfirmed_fields[0].raw_value" in removed
    _no_identifier(removed)
    assert r.redact_vehicle_identifiers(redacted) == (redacted, [])     # nothing left: idempotent


def test_the_operator_reference_must_be_opaque():
    assert r.valid_operator_reference("op-7f3a9c21")
    for bad in (None, "", "court", "nom.prenom@exemple.fr", "Jean Dupont", "x" * 65):
        assert not r.valid_operator_reference(bad), bad


# --- 2. the governed operation, on the database -------------------------------------------------------------------

pytestmark_db = pytest.mark.skipif(not check_db_connection(), reason="PostgreSQL not available")


@pytest.fixture
def operator():
    return AuthorityContext(granted=frozenset({RunnerAuthority.REDACT_ARTIFACT}), actor_reference="op-test-0001")


def _execution(session, authority):
    contact = Contact(contact_type="PERSON", display_name="B6 Redaction")
    asset = Asset(asset_domain="AUTOMOTIVE", asset_type="PASSENGER_CAR", asset_status="ACTIVE")
    session.add_all([contact, asset])
    session.flush()
    case = Case(primary_contact_id=contact.contact_id, asset_id=asset.asset_id, domain="AUTOMOTIVE", case_type="DIAGNOSTIC")
    session.add(case)
    session.flush()
    if session.get(RunnerArtifactSchemaDefinition, ("vir_resolution", "1")) is None:
        session.add(RunnerArtifactSchemaDefinition(schema_name="vir_resolution", schema_version="1",
                                                   required_fields=["resolution_id", "resolution_status"],
                                                   field_types={"resolution_id": "string"}))
    session.commit()
    result = admit_execution(session, case_id=case.case_id, asset_id=asset.asset_id, runner_type="VIR",
                             runner_version="1.0", authority=authority)
    session.commit()
    return result.object_id


def _register(session, authority, execution_id, payload, artifact_type="vir_resolution", schema="vir_resolution"):
    result = register_artifact(session, execution_id=execution_id, artifact_type=artifact_type, schema_name=schema,
                               schema_version="1", payload=payload, semantic_function="DOMAIN_ASSERTION_CARRIER",
                               lifecycle_role="FINAL", presentation_role="INTERNAL", authority=authority)
    session.commit()
    return session.get(RunnerArtifact, result.object_id)


@pytestmark_db
def test_expurgation_keeps_identity_links_and_traces_without_values(db_session, full_b6_authority, operator):
    x = _execution(db_session, full_b6_authority)
    artifact = _register(db_session, full_b6_authority, x, vir_payload())
    other = _register(db_session, full_b6_authority, x, {"resolution_id": "R", "resolution_status": "resolved",
                                                         "note": VIN}, artifact_type="pgdr_result", schema="vir_resolution")
    registered_hash = artifact.content_hash
    assert r.classify_integrity(db_session, artifact) == r.IntegrityClass.ORIGINAL_INTACT

    result = r.redact_artifact_identifiers(db_session, artifact_id=artifact.artifact_id, reason="RETENTION_POLICY",
                                           authority=operator)
    db_session.commit()
    assert result.outcome == RunnerOutcome.SUCCESS and result.payload["redacted"] == [str(artifact.artifact_id)]
    db_session.refresh(artifact)
    _no_identifier(artifact.payload)
    assert artifact.payload["resolution_id"] == "VIR-RES-FICTIF-1" and artifact.execution_id == x
    assert artifact.artifact_status == "VALIDATED" and artifact.redaction_status == "REDACTED"
    assert artifact.content_hash == compute_content_hash(artifact.payload) != registered_hash   # REQ-B6-054 holds
    record = db_session.get(RunnerArtifactRedaction, artifact.artifact_id)
    assert record.original_content_hash == registered_hash and record.redacted_content_hash == artifact.content_hash
    assert record.operation == "VEHICLE_IDENTIFIER_REDACTION" and record.reason == "RETENTION_POLICY"
    assert record.operator_reference == "op-test-0001" and record.redacted_at is not None
    decision = db_session.get(RunnerGovernanceDecision, record.decision_id)
    assert decision.decision_type == "ARTIFACT_REDACTION" and decision.artifact_id == artifact.artifact_id
    assert decision.prior_value["content_hash"] == registered_hash
    # No removed value and no copy of the removed content anywhere in the trace.
    _no_identifier([record.redacted_locations, decision.prior_value, decision.new_value, decision.authority_context])
    assert r.classify_integrity(db_session, artifact) == r.IntegrityClass.REDACTED_AUTHORIZED
    # Not eligible: another artifact type is never touched, even holding the same value.
    db_session.refresh(other)
    assert other.payload["note"] == VIN and other.redaction_status is None
    assert r.redact_artifact_identifiers(db_session, artifact_id=other.artifact_id, reason="RETENTION_POLICY",
                                         authority=operator).outcome == RunnerOutcome.SEMANTIC_REJECTION
    assert r.classify_integrity(db_session, other) == r.IntegrityClass.ORIGINAL_INTACT

    # Idempotent: nothing more is written.
    again = r.redact_artifact_identifiers(db_session, artifact_id=artifact.artifact_id, reason="RETENTION_POLICY",
                                          authority=operator)
    db_session.commit()
    assert again.outcome == RunnerOutcome.NO_CHANGE
    assert db_session.query(RunnerArtifactRedaction).filter_by(artifact_id=artifact.artifact_id).count() == 1
    assert db_session.query(RunnerGovernanceDecision).filter_by(artifact_id=artifact.artifact_id,
                                                                decision_type="ARTIFACT_REDACTION").count() == 1


@pytestmark_db
def test_every_linked_version_is_expurgated_in_the_same_operation(db_session, full_b6_authority, operator):
    x = _execution(db_session, full_b6_authority)
    v1 = _register(db_session, full_b6_authority, x, vir_payload("R-1"))
    v2_id = supersede_artifact(db_session, old_artifact_id=v1.artifact_id, new_payload=vir_payload("R-2"),
                               authority=full_b6_authority).object_id
    db_session.commit()
    v3_id = supersede_artifact(db_session, old_artifact_id=v2_id, new_payload=vir_payload("R-3"),
                               authority=full_b6_authority).object_id
    db_session.commit()
    # Asked on the middle version: the older and the newer ones go too.
    result = r.redact_artifact_identifiers(db_session, artifact_id=v2_id, reason="DATA_SUBJECT_REQUEST", authority=operator)
    db_session.commit()
    assert result.outcome == RunnerOutcome.SUCCESS and len(result.payload["redacted"]) == 3
    operations = set()
    for artifact_id, status, rid in ((v1.artifact_id, "SUPERSEDED", "R-1"), (v2_id, "SUPERSEDED", "R-2"),
                                     (v3_id, "VALIDATED", "R-3")):
        a = db_session.get(RunnerArtifact, artifact_id)
        db_session.refresh(a)
        _no_identifier(a.payload)
        assert a.artifact_status == status and a.payload["resolution_id"] == rid and a.redaction_status == "REDACTED"
        assert r.classify_integrity(db_session, a) == r.IntegrityClass.REDACTED_AUTHORIZED
        operations.add(db_session.get(RunnerArtifactRedaction, artifact_id).operation_id)
    assert len(operations) == 1
    assert db_session.get(RunnerArtifact, v3_id).supersedes_artifact_id == v2_id
    assert check_supersession_consistency(db_session) == []              # REQ-B6-057 unaffected


@pytestmark_db
def test_integrity_tells_intact_expurgated_and_altered_apart(db_session, full_b6_authority, operator):
    x = _execution(db_session, full_b6_authority)
    intact = _register(db_session, full_b6_authority, x, vir_payload("I"))
    altered = _register(db_session, full_b6_authority, x, vir_payload("A"))
    redacted = _register(db_session, full_b6_authority, x, vir_payload("E"))
    r.redact_artifact_identifiers(db_session, artifact_id=redacted.artifact_id, reason="RETENTION_POLICY", authority=operator)
    db_session.commit()
    # Failure injection (never done by real code): direct changes outside the governed operation.
    db_session.execute(text("UPDATE cpl.runner_artifacts SET payload = jsonb_set(payload, '{resolution_id}', '\"X\"') "
                            "WHERE artifact_id = :a"), {"a": altered.artifact_id})
    db_session.commit()
    for a in (intact, altered, redacted):
        db_session.refresh(a)
    assert r.classify_integrity(db_session, intact) == r.IntegrityClass.ORIGINAL_INTACT
    assert r.classify_integrity(db_session, redacted) == r.IntegrityClass.REDACTED_AUTHORIZED
    assert r.classify_integrity(db_session, altered) == r.IntegrityClass.UNAUTHORIZED_ALTERATION
    # An altered artifact is never laundered by an expurgation: refused, nothing written.
    refused = r.redact_artifact_identifiers(db_session, artifact_id=altered.artifact_id, reason="RETENTION_POLICY",
                                            authority=operator)
    assert refused.outcome == RunnerOutcome.CONFLICT and db_session.get(RunnerArtifactRedaction, altered.artifact_id) is None
    # An expurgated artifact changed afterwards, or a mark without its record, is an alteration too.
    db_session.execute(text("UPDATE cpl.runner_artifacts SET payload = jsonb_set(payload, '{resolution_id}', '\"Y\"') "
                            "WHERE artifact_id = :a"), {"a": redacted.artifact_id})
    db_session.execute(text("UPDATE cpl.runner_artifacts SET redaction_status = 'REDACTED' WHERE artifact_id = :a"),
                       {"a": intact.artifact_id})
    db_session.commit()
    for a in (intact, redacted):
        db_session.refresh(a)
    assert r.classify_integrity(db_session, redacted) == r.IntegrityClass.UNAUTHORIZED_ALTERATION
    assert r.classify_integrity(db_session, intact) == r.IntegrityClass.UNAUTHORIZED_ALTERATION
    audit = r.audit_integrity(db_session)
    assert {intact.artifact_id, altered.artifact_id, redacted.artifact_id} <= set(audit[r.IntegrityClass.UNAUTHORIZED_ALTERATION])


@pytestmark_db
def test_authority_reason_and_operator_are_required(db_session, full_b6_authority, operator):
    x = _execution(db_session, full_b6_authority)
    a = _register(db_session, full_b6_authority, x, vir_payload())
    assert r.redact_artifact_identifiers(db_session, artifact_id=a.artifact_id, reason="RETENTION_POLICY",
                                         authority=full_b6_authority).outcome == RunnerOutcome.AUTHORITY_REJECTION
    assert r.redact_artifact_identifiers(db_session, artifact_id=a.artifact_id, reason="parce que",
                                         authority=operator).outcome == RunnerOutcome.SEMANTIC_REJECTION
    named = AuthorityContext(granted=frozenset({RunnerAuthority.REDACT_ARTIFACT}), actor_reference="jean@exemple.fr")
    assert r.redact_artifact_identifiers(db_session, artifact_id=a.artifact_id, reason="RETENTION_POLICY",
                                         authority=named).outcome == RunnerOutcome.SEMANTIC_REJECTION
    db_session.refresh(a)
    assert a.redaction_status is None and a.payload == vir_payload()


@pytestmark_db
def test_the_command_simulates_by_default_and_prints_no_value(db_session, full_b6_authority):
    x = _execution(db_session, full_b6_authority)
    a = _register(db_session, full_b6_authority, x, vir_payload())
    factory = sessionmaker(bind=db_session.get_bind())
    out = io.StringIO()
    assert run_command(["--motif", "RETENTION_POLICY", "--operateur", "op-test-0002", "--artefact", str(a.artifact_id)],
                       session_factory=factory, out=out) == 0
    db_session.refresh(a)
    assert a.redaction_status is None and a.payload == vir_payload()          # simulation: nothing written
    assert "simulation" in out.getvalue() and f"à expurger {a.artifact_id}" in out.getvalue()
    out = io.StringIO()
    assert run_command(["--motif", "RETENTION_POLICY", "--operateur", "op-test-0002", "--artefact", str(a.artifact_id),
                        "--executer"], session_factory=factory, out=out) == 0
    db_session.expire_all()
    a = db_session.get(RunnerArtifact, a.artifact_id)
    assert a.redaction_status == "REDACTED" and "1 artefact(s) expurgé(s)" in out.getvalue()
    _no_identifier(a.payload)
    out = io.StringIO()
    assert run_command(["--motif", "RETENTION_POLICY", "--operateur", "op-test-0002", "--artefact", str(a.artifact_id),
                        "--executer"], session_factory=factory, out=out) == 0
    assert "à expurger : 0" in out.getvalue() and "déjà expurgés : 1" in out.getvalue()
    assert run_command(["--motif", "RETENTION_POLICY", "--operateur", "nom@exemple.fr"], session_factory=factory,
                       out=io.StringIO()) == 2
    for value in (VIN, PLATE, OTHER_VIN):
        assert value not in out.getvalue()
