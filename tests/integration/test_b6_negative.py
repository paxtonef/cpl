"""B6 Negative Verification. Traces to REQ-B6-* per
B6_EXECUTION_ARTIFACT_REQUIREMENT_MATRIX_v0.1.md."""
import uuid

import pytest

from app.cpl.models.contact import Contact
from app.cpl.models.asset import Asset
from app.cpl.models.case import Case
from app.cpl.models.runner_execution import RunnerExecution
from app.cpl.models.runner_artifact import RunnerArtifact
from app.cpl.models.runner_artifact_schema_definition import RunnerArtifactSchemaDefinition
from app.cpl.runners.execution import admit_execution, transition_status, persist_runner_report
from app.cpl.runners.artifacts import register_artifact, supersede_artifact
from app.cpl.runners.classification import validate_classification, ClassificationValidationOutcome
from app.cpl.runners.outcomes import RunnerOutcome
from app.cpl.identity.authority import AuthorityContext
from app.db.engine import check_db_connection

pytestmark = pytest.mark.skipif(not check_db_connection(), reason="PostgreSQL not available")


def _contact(session):
    c = Contact(contact_type="PERSON", display_name="B6 Negative Contact")
    session.add(c)
    session.flush()
    return c


def _asset(session):
    a = Asset(asset_domain="AUTOMOTIVE", asset_type="PASSENGER_CAR", asset_status="ACTIVE")
    session.add(a)
    session.flush()
    return a


def _case(session, contact, asset):
    c = Case(primary_contact_id=contact.contact_id, asset_id=asset.asset_id, domain="AUTOMOTIVE", case_type="DIAGNOSTIC")
    session.add(c)
    session.flush()
    return c


def _schema_def(session, name="vir.identity.v1", version="1"):
    d = RunnerArtifactSchemaDefinition(schema_name=name, schema_version=version,
                                        required_fields=["vin", "confidence"],
                                        field_types={"vin": "string", "confidence": "number"})
    session.add(d)
    session.flush()
    return d


class TestB6Negative:

    # --- Authority (REQ-B6-014..017, 022, 076..079) ---

    def test_n01_admission_without_authority_is_rejected(self, db_session):
        contact = _contact(db_session)
        asset = _asset(db_session)
        case = _case(db_session, contact, asset)
        db_session.commit()

        empty_authority = AuthorityContext(granted=frozenset(), actor_reference="unauthorized")
        result = admit_execution(db_session, case_id=case.case_id, asset_id=asset.asset_id, runner_type="VIR",
                                  runner_version="1.0", authority=empty_authority)
        assert result.outcome == RunnerOutcome.AUTHORITY_REJECTION
        # No row created — REQ-B6-076/009 "no row" case.
        assert db_session.query(RunnerExecution).filter(RunnerExecution.case_id == case.case_id).count() == 0

    def test_n02_initiator_alone_does_not_grant_authority(self, db_session, full_b6_authority):
        """REQ-B6-014/022: initiated_by_contact_id is attribution only —
        recording it never substitutes for the ADMIT_EXECUTION grant."""
        contact = _contact(db_session)
        asset = _asset(db_session)
        case = _case(db_session, contact, asset)
        db_session.commit()

        no_admit_authority = AuthorityContext(granted=frozenset({"TRANSITION_EXECUTION_STATUS"}), actor_reference="partial")
        result = admit_execution(db_session, case_id=case.case_id, asset_id=asset.asset_id, runner_type="VIR",
                                  runner_version="1.0", initiated_by_contact_id=contact.contact_id,
                                  authority=no_admit_authority)
        assert result.outcome == RunnerOutcome.AUTHORITY_REJECTION

    # --- Idempotency conflict (REQ-B6-037/038) ---

    def test_n03_same_key_incompatible_intent_conflicts(self, db_session, full_b6_authority):
        contact = _contact(db_session)
        asset = _asset(db_session)
        case1 = _case(db_session, contact, asset)
        asset2 = _asset(db_session)
        case2 = _case(db_session, contact, asset2)
        db_session.commit()
        key = str(uuid.uuid4())

        r1 = admit_execution(db_session, case_id=case1.case_id, asset_id=asset.asset_id, runner_type="VIR",
                              runner_version="1.0", idempotency_key=key, authority=full_b6_authority)
        db_session.commit()
        assert r1.outcome == RunnerOutcome.SUCCESS

        r2 = admit_execution(db_session, case_id=case2.case_id, asset_id=asset2.asset_id, runner_type="VIR",
                              runner_version="1.0", idempotency_key=key, authority=full_b6_authority)
        db_session.commit()
        assert r2.outcome == RunnerOutcome.CONFLICT
        # No silent overwrite: original row's case_id is untouched.
        assert db_session.get(RunnerExecution, r1.object_id).case_id == case1.case_id

    # --- Lifecycle transition validity (REQ-B6-009) ---

    def test_n04_invalid_transition_rejected(self, db_session, full_b6_authority):
        contact = _contact(db_session)
        asset = _asset(db_session)
        case = _case(db_session, contact, asset)
        db_session.commit()
        r1 = admit_execution(db_session, case_id=case.case_id, asset_id=asset.asset_id, runner_type="VIR",
                              runner_version="1.0", authority=full_b6_authority)
        db_session.commit()

        # CREATED -> COMPLETED is not in the frozen transition table.
        result = transition_status(db_session, execution_id=r1.object_id, new_status="COMPLETED", authority=full_b6_authority)
        db_session.commit()
        assert result.outcome == RunnerOutcome.SEMANTIC_REJECTION
        assert db_session.get(RunnerExecution, r1.object_id).execution_status == "CREATED"

    def test_n05_terminal_state_rejects_further_transition(self, db_session, full_b6_authority):
        contact = _contact(db_session)
        asset = _asset(db_session)
        case = _case(db_session, contact, asset)
        db_session.commit()
        r1 = admit_execution(db_session, case_id=case.case_id, asset_id=asset.asset_id, runner_type="VIR",
                              runner_version="1.0", authority=full_b6_authority)
        db_session.commit()
        transition_status(db_session, execution_id=r1.object_id, new_status="CANCELLED", authority=full_b6_authority)
        db_session.commit()

        result = transition_status(db_session, execution_id=r1.object_id, new_status="RUNNING", authority=full_b6_authority)
        db_session.commit()
        assert result.outcome == RunnerOutcome.SEMANTIC_REJECTION

    def test_n06_persist_runner_report_rejects_non_runner_reportable_status(self, db_session, full_b6_authority):
        contact = _contact(db_session)
        asset = _asset(db_session)
        case = _case(db_session, contact, asset)
        db_session.commit()
        r1 = admit_execution(db_session, case_id=case.case_id, asset_id=asset.asset_id, runner_type="VIR",
                              runner_version="1.0", authority=full_b6_authority)
        db_session.commit()
        with pytest.raises(ValueError):
            persist_runner_report(db_session, execution_id=r1.object_id, new_status="CANCELLED", authority=full_b6_authority)

    # --- Artifact classification (REQ-B6-090) ---

    def test_n07_missing_classification_dimension_rejected(self, db_session, full_b6_authority):
        contact = _contact(db_session)
        asset = _asset(db_session)
        case = _case(db_session, contact, asset)
        db_session.commit()
        _schema_def(db_session)
        r1 = admit_execution(db_session, case_id=case.case_id, asset_id=asset.asset_id, runner_type="VIR",
                              runner_version="1.0", authority=full_b6_authority)
        db_session.commit()

        result = register_artifact(db_session, execution_id=r1.object_id, artifact_type="vin_result",
                                    schema_name="vir.identity.v1", schema_version="1",
                                    payload={"vin": "1HGCM82633A004352", "confidence": 0.9},
                                    semantic_function="DOMAIN_DETERMINATION_CARRIER", lifecycle_role="FINAL",
                                    presentation_role=None, authority=full_b6_authority)
        db_session.commit()
        assert result.outcome == RunnerOutcome.SEMANTIC_REJECTION
        assert db_session.query(RunnerArtifact).filter(RunnerArtifact.execution_id == r1.object_id).count() == 0

    def test_n08_invalid_classification_value_rejected(self, db_session, full_b6_authority):
        contact = _contact(db_session)
        asset = _asset(db_session)
        case = _case(db_session, contact, asset)
        db_session.commit()
        _schema_def(db_session)
        r1 = admit_execution(db_session, case_id=case.case_id, asset_id=asset.asset_id, runner_type="VIR",
                              runner_version="1.0", authority=full_b6_authority)
        db_session.commit()

        result = register_artifact(db_session, execution_id=r1.object_id, artifact_type="vin_result",
                                    schema_name="vir.identity.v1", schema_version="1",
                                    payload={"vin": "1HGCM82633A004352", "confidence": 0.9},
                                    semantic_function="NOT_A_REAL_VALUE", lifecycle_role="FINAL",
                                    presentation_role="INTERNAL", authority=full_b6_authority)
        assert result.outcome == RunnerOutcome.SEMANTIC_REJECTION

    def test_n09_classification_taxonomy_five_outcomes_distinguishable(self):
        """REQ-B6-090: no two outcomes collapse into the same result."""
        r_missing = validate_classification(semantic_function=None, lifecycle_role="FINAL", presentation_role="INTERNAL")
        r_invalid = validate_classification(semantic_function="BOGUS", lifecycle_role="FINAL", presentation_role="INTERNAL")
        r_valid = validate_classification(semantic_function="EXECUTION_OUTPUT_CARRIER", lifecycle_role="FINAL", presentation_role="INTERNAL")
        assert r_missing.outcome == ClassificationValidationOutcome.MISSING_REQUIRED_DIMENSION
        assert r_invalid.outcome == ClassificationValidationOutcome.INVALID_VALUE
        assert r_valid.outcome == ClassificationValidationOutcome.VALID
        assert len({r_missing.outcome, r_invalid.outcome, r_valid.outcome}) == 3

    # --- Structural validation / REJECTED semantics (REQ-B6-033, 089) ---

    def test_n10_unregistered_schema_routes_to_rejected(self, db_session, full_b6_authority):
        contact = _contact(db_session)
        asset = _asset(db_session)
        case = _case(db_session, contact, asset)
        db_session.commit()
        r1 = admit_execution(db_session, case_id=case.case_id, asset_id=asset.asset_id, runner_type="VIR",
                              runner_version="1.0", authority=full_b6_authority)
        db_session.commit()

        result = register_artifact(db_session, execution_id=r1.object_id, artifact_type="vin_result",
                                    schema_name="vir.unknown_schema", schema_version="99",
                                    payload={"vin": "1HGCM82633A004352", "confidence": 0.9},
                                    semantic_function="DOMAIN_DETERMINATION_CARRIER", lifecycle_role="FINAL",
                                    presentation_role="INTERNAL", authority=full_b6_authority)
        db_session.commit()
        assert result.outcome == RunnerOutcome.SUCCESS  # registration itself succeeds
        artifact = db_session.get(RunnerArtifact, result.object_id)
        assert artifact.artifact_status == "REJECTED"  # structural rejection, never domain

    def test_n11_missing_required_field_routes_to_rejected(self, db_session, full_b6_authority):
        contact = _contact(db_session)
        asset = _asset(db_session)
        case = _case(db_session, contact, asset)
        db_session.commit()
        _schema_def(db_session)
        r1 = admit_execution(db_session, case_id=case.case_id, asset_id=asset.asset_id, runner_type="VIR",
                              runner_version="1.0", authority=full_b6_authority)
        db_session.commit()

        result = register_artifact(db_session, execution_id=r1.object_id, artifact_type="vin_result",
                                    schema_name="vir.identity.v1", schema_version="1",
                                    payload={"vin": "1HGCM82633A004352"},  # missing "confidence"
                                    semantic_function="DOMAIN_DETERMINATION_CARRIER", lifecycle_role="FINAL",
                                    presentation_role="INTERNAL", authority=full_b6_authority)
        db_session.commit()
        artifact = db_session.get(RunnerArtifact, result.object_id)
        assert artifact.artifact_status == "REJECTED"

    # --- Supersession preconditions (REQ-B6-034/057) ---

    def test_n12_only_validated_artifact_may_be_superseded(self, db_session, full_b6_authority):
        contact = _contact(db_session)
        asset = _asset(db_session)
        case = _case(db_session, contact, asset)
        db_session.commit()
        r1 = admit_execution(db_session, case_id=case.case_id, asset_id=asset.asset_id, runner_type="VIR",
                              runner_version="1.0", authority=full_b6_authority)
        db_session.commit()
        rejected = register_artifact(db_session, execution_id=r1.object_id, artifact_type="vin_result",
                                      schema_name="vir.unknown_schema", schema_version="99",
                                      payload={"vin": "x"}, semantic_function="DOMAIN_DETERMINATION_CARRIER",
                                      lifecycle_role="FINAL", presentation_role="INTERNAL", authority=full_b6_authority)
        db_session.commit()

        result = supersede_artifact(db_session, old_artifact_id=rejected.object_id, new_payload={"vin": "y"},
                                     authority=full_b6_authority)
        assert result.outcome == RunnerOutcome.SEMANTIC_REJECTION

    # --- parent_execution_id negative boundary (REQ-B6-006, 043..045) ---

    def test_n13_parent_execution_id_never_referenced_by_any_b6_logic(self):
        """REQ-B6-043: static confirmation that no B6 service module reads
        or branches on parent_execution_id anywhere in executable logic.
        Documentation strings are permitted to name the field when
        explaining the prohibition itself (exactly as this Build Unit's
        own governance documents do) — what must never appear is an
        attribute access or comparison against it."""
        import app.cpl.runners.execution as execution_module
        import app.cpl.runners.idempotency as idempotency_module
        import app.cpl.runners.artifacts as artifacts_module
        import ast
        import inspect

        for module in (execution_module, idempotency_module, artifacts_module):
            tree = ast.parse(inspect.getsource(module))
            for node in ast.walk(tree):
                if isinstance(node, ast.Attribute) and node.attr == "parent_execution_id":
                    pytest.fail(f"{module.__name__} accesses .parent_execution_id in executable code")
                if isinstance(node, ast.Name) and node.id == "parent_execution_id":
                    pytest.fail(f"{module.__name__} references parent_execution_id as an identifier in executable code")

    def test_n14_self_parent_rejected_by_constraint(self, db_session, full_b6_authority):
        contact = _contact(db_session)
        asset = _asset(db_session)
        case = _case(db_session, contact, asset)
        db_session.commit()
        r1 = admit_execution(db_session, case_id=case.case_id, asset_id=asset.asset_id, runner_type="VIR",
                              runner_version="1.0", authority=full_b6_authority)
        db_session.commit()
        execution = db_session.get(RunnerExecution, r1.object_id)
        execution.parent_execution_id = execution.execution_id
        from sqlalchemy.exc import IntegrityError
        with pytest.raises(IntegrityError):
            db_session.flush()
