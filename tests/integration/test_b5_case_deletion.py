"""REQ-B5-116 — governed deletion of an expired Case.

Fictitious data only, on the test database (each test runs in a transaction
rolled back at the end).
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.automotive.models.vehicle_detail import VehicleDetail
from app.cpl.cases import deletion as d
from app.cpl.cases.events import record_case_event, register_event_type
from app.cpl.cases.lifecycle import create_case
from app.cpl.cases.outcomes import CaseOutcome
from app.cpl.cases.participants import add_participant
from app.cpl.identity.authority import AuthorityContext
from app.cpl.models.asset import Asset
from app.cpl.models.asset_identity_resolution import AssetIdentityResolution
from app.cpl.models.canonical_case_decision import CanonicalCaseDecision
from app.cpl.models.case import Case
from app.cpl.models.case_deletion import CaseDeletion
from app.cpl.models.case_event import CaseEvent
from app.cpl.models.contact import Contact
from app.cpl.models.contact_asset_relationship import ContactAssetRelationship
from app.cpl.models.manufacturer_knowledge_document import ManufacturerKnowledgeDocument
from app.cpl.models.runner_artifact import RunnerArtifact
from app.cpl.models.runner_artifact_redaction import RunnerArtifactRedaction
from app.cpl.models.runner_artifact_schema_definition import RunnerArtifactSchemaDefinition
from app.cpl.models.runner_execution import RunnerExecution
from app.cpl.models.runner_execution_correction import RunnerExecutionCorrection
from app.cpl.models.runner_governance_decision import RunnerGovernanceDecision
from app.cpl.runners import redaction
from app.cpl.runners.artifacts import register_artifact, supersede_artifact
from app.cpl.runners.correction import correct_execution_metadata
from app.cpl.runners.execution import admit_execution
from app.db.engine import check_db_connection

pytestmark = pytest.mark.skipif(not check_db_connection(), reason="PostgreSQL not available")

VIN = "VF3FICTIF0DEL0042"
PLATE = "ZZ-116-ZZ"
DAYS = 30
NOW = datetime.now(timezone.utc)
CUTOFF = NOW - timedelta(days=DAYS)


@pytest.fixture
def operator():
    return AuthorityContext(granted=frozenset({d.CaseAuthority.DELETE_EXPIRED_CASE}), actor_reference="pi-purge:op-0001")


@pytest.fixture
def everything(full_b4_authority, full_b5_authority, full_b6_authority):
    granted = (full_b4_authority.granted | full_b5_authority.granted | full_b6_authority.granted
               | {redaction.RunnerAuthority.REDACT_ARTIFACT})
    return AuthorityContext(granted=frozenset(granted), actor_reference="test-suite-0001")


def _vehicle(session):
    contact = Contact(contact_type="PERSON", display_name="B5 Deletion")
    asset = Asset(asset_domain="AUTOMOTIVE", asset_type="PASSENGER_CAR", asset_status="ACTIVE")
    session.add_all([contact, asset])
    session.flush()
    session.add(ContactAssetRelationship(contact_id=contact.contact_id, asset_id=asset.asset_id,
                                         relationship_type="OWNER", relationship_status="ACTIVE", source="test"))
    for name in ("vir_resolution", "pgdr_v1_premier_constat"):
        if session.get(RunnerArtifactSchemaDefinition, (name, "1")) is None:
            session.add(RunnerArtifactSchemaDefinition(schema_name=name, schema_version="1",
                                                       required_fields=["resolution_id"],
                                                       field_types={"resolution_id": "string"}))
    register_event_type(session, event_type="B5_DELETION_TEST", semantic_class="CPL_OPERATIONAL_FACT")
    session.commit()
    return contact, asset


def _case(session, authority, contact, asset, *, age_days: int):
    """A Case with everything the product records for it: governed creation,
    a participant, a VIR execution (resolution, artifact in two versions, one
    expurgated), a notice execution with its Premier Constat, a correction
    and an event."""
    case_id = create_case(session, primary_contact_id=contact.contact_id, asset_id=asset.asset_id,
                          domain="AUTOMOTIVE", case_type="DIAGNOSTIC", authority=authority,
                          idempotency_key=str(uuid.uuid4())).object_id
    add_participant(session, case_id=case_id, contact_id=contact.contact_id, participant_role="REQUESTER",
                    authority=authority, idempotency_key=str(uuid.uuid4()))
    vir = admit_execution(session, case_id=case_id, asset_id=asset.asset_id, runner_type="VIR",
                          runner_version="1.0", authority=authority).object_id
    resolution = AssetIdentityResolution(asset_id=asset.asset_id, resolver_type="VIR", resolver_version="1.0",
                                         execution_id=vir, resolution_status="RESOLVED",
                                         canonical_identity_payload={"identifiers": {"vin": VIN,
                                                                                     "registration_number": PLATE}})
    session.add(resolution)
    session.flush()
    payload = {"resolution_id": f"R-{case_id}", "vehicle_identity": {"identifiers": {"vin": VIN}}}
    first = register_artifact(session, execution_id=vir, artifact_type="vir_resolution", schema_name="vir_resolution",
                              schema_version="1", payload=payload, semantic_function="DOMAIN_ASSERTION_CARRIER",
                              lifecycle_role="FINAL", presentation_role="INTERNAL", authority=authority).object_id
    second = supersede_artifact(session, old_artifact_id=first, new_payload={**payload, "v": 2},
                                authority=authority).object_id
    redaction.redact_artifact_identifiers(session, artifact_id=second, reason="RETENTION_POLICY", authority=authority)
    notice = admit_execution(session, case_id=case_id, asset_id=asset.asset_id, runner_type="PGDR_V1_NOTICE",
                             runner_version="pgdr-v1", authority=authority).object_id
    register_artifact(session, execution_id=notice, artifact_type="pgdr_v1_premier_constat",
                      schema_name="pgdr_v1_premier_constat", schema_version="1",
                      payload={"resolution_id": "-", "premier_constat": "fictif"},
                      semantic_function="DOMAIN_DETERMINATION_CARRIER", lifecycle_role="FINAL",
                      presentation_role="INTERNAL", authority=authority)
    correct_execution_metadata(session, execution_id=notice, field_name="runner_version", new_value="pgdr-v1b",
                               authority=authority)
    record_case_event(session, case_id=case_id, event_type="B5_DELETION_TEST", actor_type="SYSTEM",
                      execution_id=vir, authority=authority)
    case = session.get(Case, case_id)
    case.current_execution_id = notice
    case.created_at = NOW - timedelta(days=age_days)
    session.commit()
    return case_id, resolution.resolution_id


def _rows(session, case_id):
    fp = d.case_footprint(session, case_id)
    return {k: v for k, v in fp.counts().items() if k != "cases"} | {"cases": int(session.get(Case, case_id) is not None)}


def test_case_within_its_period_is_untouched_and_expired_case_is_deleted(db_session, everything, operator):
    contact, asset = _vehicle(db_session)
    kept_id, _ = _case(db_session, everything, contact, asset, age_days=DAYS - 1)
    old_id, old_resolution = _case(db_session, everything, contact, asset, age_days=DAYS + 10)
    db_session.add(VehicleDetail(asset_id=asset.asset_id, make="Peugeot", model="3008", vin_display=VIN,
                                 source_resolution_id=old_resolution))
    db_session.commit()
    knowledge = db_session.query(ManufacturerKnowledgeDocument).count()
    before_kept = _rows(db_session, kept_id)
    old_rows = _rows(db_session, old_id)
    assert old_rows["runner_artifacts"] == 3 and old_rows["runner_artifact_redactions"] == 2   # both versions (REQ-B6-091)
    assert old_rows["case_events"] == 1 and old_rows["runner_execution_corrections"] == 1

    # Within its period: refused, nothing modified.
    r = d.delete_expired_case(db_session, case_id=kept_id, created_before=CUTOFF, retention_days=DAYS, authority=operator)
    assert r.outcome == CaseOutcome.SEMANTIC_REJECTION and "within its retention period" in r.detail
    assert _rows(db_session, kept_id) == before_kept

    plan = d.plan_expired_cases(db_session, created_before=CUTOFF)
    assert old_id in plan.due and kept_id not in plan.due and kept_id not in plan.blocked

    r = d.delete_expired_case(db_session, case_id=old_id, created_before=CUTOFF, retention_days=DAYS,
                              authority=operator)
    db_session.commit()
    assert r.outcome == CaseOutcome.SUCCESS
    assert db_session.get(Case, old_id) is None
    for model, column in ((RunnerExecution, RunnerExecution.case_id), (CaseEvent, CaseEvent.case_id),
                          (CanonicalCaseDecision, CanonicalCaseDecision.case_id)):
        assert db_session.query(model).filter(column == old_id).count() == 0
    assert db_session.get(AssetIdentityResolution, old_resolution) is None
    # The trace: counts, period, operator, operation; no content, no contact, no vehicle, no identifier.
    trace = db_session.get(CaseDeletion, old_id)
    assert trace.deleted_counts == old_rows and trace.retention_days == DAYS and trace.anchor == "creation_dossier"
    assert trace.operator_reference == "pi-purge:op-0001" and str(trace.operation_id) == r.payload["operation_id"]
    dumped = json.dumps({c.name: str(getattr(trace, c.name)) for c in CaseDeletion.__table__.columns})
    for value in (VIN, PLATE, str(contact.contact_id), str(asset.asset_id), "fictif", "Peugeot"):
        assert value not in dumped
    # Preserved: the account's contact, the vehicle, its summary (source cleared), the other case, knowledge.
    db_session.expire_all()
    assert db_session.get(Contact, contact.contact_id) is not None and db_session.get(Asset, asset.asset_id) is not None
    assert db_session.query(ContactAssetRelationship).filter_by(asset_id=asset.asset_id).count() == 1
    detail = db_session.get(VehicleDetail, asset.asset_id)
    assert detail.model == "3008" and detail.source_resolution_id is None
    assert _rows(db_session, kept_id) == before_kept
    assert db_session.query(ManufacturerKnowledgeDocument).count() == knowledge
    assert redaction.audit_integrity(db_session)[redaction.IntegrityClass.UNAUTHORIZED_ALTERATION] == []

    # Second run: no further effect, no second trace.
    again = d.delete_expired_case(db_session, case_id=old_id, created_before=CUTOFF, retention_days=DAYS,
                                  authority=operator)
    assert again.outcome == CaseOutcome.NO_CHANGE
    assert db_session.query(CaseDeletion).filter_by(case_id=old_id).count() == 1


def test_a_case_another_row_depends_on_is_not_deleted(db_session, everything, operator):
    contact, asset = _vehicle(db_session)
    old_id, old_resolution = _case(db_session, everything, contact, asset, age_days=DAYS + 10)
    new_id, new_resolution = _case(db_session, everything, contact, asset, age_days=1)
    db_session.get(AssetIdentityResolution, new_resolution).supersedes_resolution_id = old_resolution
    db_session.commit()
    before = _rows(db_session, old_id)
    plan = d.plan_expired_cases(db_session, created_before=CUTOFF)
    assert plan.blocked[old_id] == ["resolution of another case"] and old_id not in plan.due
    r = d.delete_expired_case(db_session, case_id=old_id, created_before=CUTOFF, retention_days=DAYS, authority=operator)
    assert r.outcome == CaseOutcome.CONFLICT and "resolution of another case" in r.detail
    assert _rows(db_session, old_id) == before and db_session.get(CaseDeletion, old_id) is None

    db_session.get(AssetIdentityResolution, new_resolution).supersedes_resolution_id = None
    db_session.get(Asset, asset.asset_id).current_identity_resolution_id = old_resolution
    db_session.commit()
    r = d.delete_expired_case(db_session, case_id=old_id, created_before=CUTOFF, retention_days=DAYS, authority=operator)
    assert r.outcome == CaseOutcome.CONFLICT and "current identity of the vehicle" in r.detail
    assert _rows(db_session, old_id) == before


def test_an_interrupted_deletion_leaves_the_case_whole_and_a_new_run_completes(db_session, everything, operator,
                                                                               monkeypatch):
    contact, asset = _vehicle(db_session)
    old_id, _ = _case(db_session, everything, contact, asset, age_days=DAYS + 10)
    before = _rows(db_session, old_id)
    real_delete = d._delete

    def failing(session, column, ids):
        if column.class_ is RunnerExecution:
            raise RuntimeError("panne simulée")
        real_delete(session, column, ids)

    monkeypatch.setattr(d, "_delete", failing)
    savepoint = db_session.begin_nested()        # the caller's transaction for this Case
    with pytest.raises(RuntimeError):
        d.delete_expired_case(db_session, case_id=old_id, created_before=CUTOFF, retention_days=DAYS, authority=operator)
    savepoint.rollback()
    db_session.expire_all()
    assert _rows(db_session, old_id) == before and db_session.get(CaseDeletion, old_id) is None

    monkeypatch.setattr(d, "_delete", real_delete)
    r = d.delete_expired_case(db_session, case_id=old_id, created_before=CUTOFF, retention_days=DAYS, authority=operator)
    db_session.commit()
    assert r.outcome == CaseOutcome.SUCCESS and r.payload["counts"] == before
    assert db_session.get(Case, old_id) is None


def test_authority_period_and_operator_are_required(db_session, everything, operator):
    contact, asset = _vehicle(db_session)
    old_id, _ = _case(db_session, everything, contact, asset, age_days=DAYS + 10)
    before = _rows(db_session, old_id)
    no_right = AuthorityContext(granted=frozenset(), actor_reference="pi-purge:op-0001")
    named = AuthorityContext(granted=operator.granted, actor_reference="jean@exemple.fr")
    for kwargs, outcome in (
            (dict(authority=no_right, retention_days=DAYS, created_before=CUTOFF), CaseOutcome.AUTHORITY_REJECTION),
            (dict(authority=operator, retention_days=0, created_before=CUTOFF), CaseOutcome.SEMANTIC_REJECTION),
            (dict(authority=operator, retention_days=None, created_before=CUTOFF), CaseOutcome.SEMANTIC_REJECTION),
            (dict(authority=operator, retention_days=DAYS, created_before=CUTOFF.replace(tzinfo=None)),
             CaseOutcome.SEMANTIC_REJECTION),
            (dict(authority=named, retention_days=DAYS, created_before=CUTOFF), CaseOutcome.SEMANTIC_REJECTION)):
        assert d.delete_expired_case(db_session, case_id=old_id, **kwargs).outcome == outcome, kwargs
    assert d.delete_expired_case(db_session, case_id=uuid.uuid4(), created_before=CUTOFF, retention_days=DAYS,
                                 authority=operator).outcome == CaseOutcome.NOT_FOUND
    assert _rows(db_session, old_id) == before


def test_the_plan_reads_only(db_session, everything):
    contact, asset = _vehicle(db_session)
    old_id, _ = _case(db_session, everything, contact, asset, age_days=DAYS + 10)
    before = _rows(db_session, old_id)
    decisions = db_session.query(RunnerGovernanceDecision).count()
    plan = d.plan_expired_cases(db_session, created_before=CUTOFF)
    assert old_id in plan.due and plan.counts["runner_artifacts"] >= 3
    assert _rows(db_session, old_id) == before and db_session.query(RunnerGovernanceDecision).count() == decisions
    assert not db_session.new and not db_session.dirty and not db_session.deleted
    assert db_session.query(RunnerExecutionCorrection).count() >= 1
    assert db_session.query(RunnerArtifactRedaction).count() >= 1 and db_session.query(RunnerArtifact).count() >= 3
