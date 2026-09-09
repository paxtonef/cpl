"""B6 Positive Verification. Traces to REQ-B6-* per
B6_EXECUTION_ARTIFACT_REQUIREMENT_MATRIX_v0.1.md."""
import uuid

import pytest

from app.cpl.models.contact import Contact
from app.cpl.models.asset import Asset
from app.cpl.models.case import Case
from app.cpl.models.runner_execution import RunnerExecution
from app.cpl.models.runner_artifact import RunnerArtifact
from app.cpl.models.runner_artifact_schema_definition import RunnerArtifactSchemaDefinition
from app.cpl.models.runner_governance_decision import RunnerGovernanceDecision
from app.cpl.runners.execution import admit_execution, transition_status, persist_runner_report, retry_execution
from app.cpl.runners.artifacts import register_artifact, supersede_artifact, check_supersession_consistency
from app.cpl.runners.correction import correct_execution_metadata, reconstruct_original_value
from app.cpl.runners.outcomes import RunnerOutcome
from app.db.engine import check_db_connection

pytestmark = pytest.mark.skipif(not check_db_connection(), reason="PostgreSQL not available")


def _contact(session, name="B6 Test Contact"):
    c = Contact(contact_type="PERSON", display_name=name)
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


def _schema_def(session, name="vir.identity.v1", version="1", required=None, types=None):
    d = RunnerArtifactSchemaDefinition(
        schema_name=name, schema_version=version,
        required_fields=required if required is not None else ["vin", "confidence"],
        field_types=types if types is not None else {"vin": "string", "confidence": "number"},
    )
    session.add(d)
    session.flush()
    return d


class TestB6Positive:

    # --- RunnerExecution identity & admission (REQ-B6-001..008a-g, 076) ---

    def test_p01_admit_execution_creates_new_identity(self, db_session, full_b6_authority):
        contact = _contact(db_session)
        asset = _asset(db_session)
        case = _case(db_session, contact, asset)
        db_session.commit()

        result = admit_execution(
            db_session, case_id=case.case_id, asset_id=asset.asset_id, runner_type="VIR",
            runner_version="1.0", initiated_by_contact_id=contact.contact_id, authority=full_b6_authority,
        )
        db_session.commit()
        assert result.outcome == RunnerOutcome.SUCCESS
        execution = db_session.get(RunnerExecution, result.object_id)
        assert execution.execution_status == "CREATED"
        assert execution.runner_type == "VIR"

    def test_p02_admission_requires_decision_record(self, db_session, full_b6_authority):
        contact = _contact(db_session)
        asset = _asset(db_session)
        case = _case(db_session, contact, asset)
        db_session.commit()

        result = admit_execution(db_session, case_id=case.case_id, asset_id=asset.asset_id, runner_type="VIR",
                                  runner_version="1.0", authority=full_b6_authority)
        db_session.commit()
        decision = db_session.get(RunnerGovernanceDecision, result.payload["decision_id"])
        assert decision.decision_type == "EXECUTION_ADMISSION"
        assert decision.decision_mode == "AUTHORITY_EVALUATION"
        assert decision.execution_id == result.object_id

    def test_p03_two_identical_requests_no_replay_rule_yield_distinct_identities(self, db_session, full_b6_authority):
        """REQ-B6-001/002/003: SAME REQUEST/INPUT/CASE/RUNNER TYPE ≠ SAME RUNNEREXECUTION."""
        contact = _contact(db_session)
        asset = _asset(db_session)
        case = _case(db_session, contact, asset)
        db_session.commit()

        r1 = admit_execution(db_session, case_id=case.case_id, asset_id=asset.asset_id, runner_type="VIR",
                              runner_version="1.0", authority=full_b6_authority)
        db_session.commit()
        r2 = admit_execution(db_session, case_id=case.case_id, asset_id=asset.asset_id, runner_type="VIR",
                              runner_version="1.0", authority=full_b6_authority)
        db_session.commit()
        assert r1.object_id != r2.object_id

    # --- Idempotency / replay / retry (REQ-B6-035..042, 088) ---

    def test_p04_duplicate_submission_same_intent_replays(self, db_session, full_b6_authority):
        contact = _contact(db_session)
        asset = _asset(db_session)
        case = _case(db_session, contact, asset)
        db_session.commit()
        key = str(uuid.uuid4())

        r1 = admit_execution(db_session, case_id=case.case_id, asset_id=asset.asset_id, runner_type="VIR",
                              runner_version="1.0", execution_purpose="identity_check", idempotency_key=key,
                              authority=full_b6_authority)
        db_session.commit()
        r2 = admit_execution(db_session, case_id=case.case_id, asset_id=asset.asset_id, runner_type="VIR",
                              runner_version="1.0", execution_purpose="identity_check", idempotency_key=key,
                              authority=full_b6_authority)
        db_session.commit()
        assert r2.outcome == RunnerOutcome.SUCCESS
        assert r2.object_id == r1.object_id
        assert r2.payload.get("replay") is True
        count = db_session.query(RunnerExecution).filter(RunnerExecution.idempotency_key == key).count()
        assert count == 1  # no duplicate row

    def test_p05_null_key_never_deduplicates(self, db_session, full_b6_authority):
        contact = _contact(db_session)
        asset = _asset(db_session)
        case = _case(db_session, contact, asset)
        db_session.commit()

        r1 = admit_execution(db_session, case_id=case.case_id, asset_id=asset.asset_id, runner_type="VIR",
                              runner_version="1.0", authority=full_b6_authority)
        db_session.commit()
        r2 = admit_execution(db_session, case_id=case.case_id, asset_id=asset.asset_id, runner_type="VIR",
                              runner_version="1.0", authority=full_b6_authority)
        db_session.commit()
        assert r1.object_id != r2.object_id

    def test_p06_retry_after_technical_failure_creates_new_identity(self, db_session, full_b6_authority):
        contact = _contact(db_session)
        asset = _asset(db_session)
        case = _case(db_session, contact, asset)
        db_session.commit()

        r1 = admit_execution(db_session, case_id=case.case_id, asset_id=asset.asset_id, runner_type="VIR",
                              runner_version="1.0", authority=full_b6_authority)
        db_session.commit()
        transition_status(db_session, execution_id=r1.object_id, new_status="RUNNING", authority=full_b6_authority)
        db_session.commit()
        persist_runner_report(db_session, execution_id=r1.object_id, new_status="FAILED", authority=full_b6_authority)
        db_session.commit()

        r2 = retry_execution(db_session, case_id=case.case_id, asset_id=asset.asset_id, runner_type="VIR",
                              runner_version="1.0", authority=full_b6_authority)
        db_session.commit()
        assert r2.object_id != r1.object_id
        assert db_session.get(RunnerExecution, r2.object_id).execution_status == "CREATED"

    # --- Execution lifecycle & authority reconciliation (REQ-B6-009..015, 077) ---

    def test_p07_valid_transition_chain(self, db_session, full_b6_authority):
        contact = _contact(db_session)
        asset = _asset(db_session)
        case = _case(db_session, contact, asset)
        db_session.commit()
        r1 = admit_execution(db_session, case_id=case.case_id, asset_id=asset.asset_id, runner_type="VIR",
                              runner_version="1.0", authority=full_b6_authority)
        db_session.commit()

        r2 = transition_status(db_session, execution_id=r1.object_id, new_status="QUEUED", authority=full_b6_authority)
        db_session.commit()
        assert r2.outcome == RunnerOutcome.SUCCESS
        r3 = transition_status(db_session, execution_id=r1.object_id, new_status="RUNNING", authority=full_b6_authority)
        db_session.commit()
        assert r3.outcome == RunnerOutcome.SUCCESS
        r4 = persist_runner_report(db_session, execution_id=r1.object_id, new_status="COMPLETED", authority=full_b6_authority)
        db_session.commit()
        assert r4.outcome == RunnerOutcome.SUCCESS
        execution = db_session.get(RunnerExecution, r1.object_id)
        assert execution.execution_status == "COMPLETED"
        assert execution.completed_at is not None

    def test_p08_repeated_transition_is_idempotent_no_op(self, db_session, full_b6_authority):
        contact = _contact(db_session)
        asset = _asset(db_session)
        case = _case(db_session, contact, asset)
        db_session.commit()
        r1 = admit_execution(db_session, case_id=case.case_id, asset_id=asset.asset_id, runner_type="VIR",
                              runner_version="1.0", authority=full_b6_authority)
        db_session.commit()
        transition_status(db_session, execution_id=r1.object_id, new_status="QUEUED", authority=full_b6_authority)
        db_session.commit()

        before_count = db_session.query(RunnerGovernanceDecision).filter(RunnerGovernanceDecision.execution_id == r1.object_id).count()
        r2 = transition_status(db_session, execution_id=r1.object_id, new_status="QUEUED", authority=full_b6_authority)
        db_session.commit()
        after_count = db_session.query(RunnerGovernanceDecision).filter(RunnerGovernanceDecision.execution_id == r1.object_id).count()
        assert r2.outcome == RunnerOutcome.SUCCESS
        assert before_count == after_count  # no new decision recorded for a no-op

    def test_p09_runner_reported_transition_decision_distinguishable_from_admission(self, db_session, full_b6_authority):
        """REQ-B6-015/077 reconciliation: the automatic decision is
        recorded and its decision_mode is distinguishable from the
        admission decision's mode."""
        contact = _contact(db_session)
        asset = _asset(db_session)
        case = _case(db_session, contact, asset)
        db_session.commit()
        r1 = admit_execution(db_session, case_id=case.case_id, asset_id=asset.asset_id, runner_type="VIR",
                              runner_version="1.0", authority=full_b6_authority)
        db_session.commit()
        admission_decision = db_session.get(RunnerGovernanceDecision, r1.payload["decision_id"])
        assert admission_decision.decision_mode == "AUTHORITY_EVALUATION"

        transition_status(db_session, execution_id=r1.object_id, new_status="RUNNING", authority=full_b6_authority)
        db_session.commit()
        r2 = persist_runner_report(db_session, execution_id=r1.object_id, new_status="COMPLETED", authority=full_b6_authority)
        db_session.commit()
        report_decision = db_session.get(RunnerGovernanceDecision, r2.payload["decision_id"])
        assert report_decision.decision_mode == "AUTOMATIC_RULE_BOUND"
        assert report_decision.decision_type == "EXECUTION_STATUS_TRANSITION"
        assert report_decision.decision_mode != admission_decision.decision_mode

    def test_p10_execution_completed_does_not_imply_domain_result(self, db_session, full_b6_authority):
        """REQ-B6-007/067: COMPLETED means only the runner reported
        finishing — no domain-truth claim is made by this layer."""
        contact = _contact(db_session)
        asset = _asset(db_session)
        case = _case(db_session, contact, asset)
        db_session.commit()
        r1 = admit_execution(db_session, case_id=case.case_id, asset_id=asset.asset_id, runner_type="VIR",
                              runner_version="1.0", authority=full_b6_authority)
        db_session.commit()
        transition_status(db_session, execution_id=r1.object_id, new_status="RUNNING", authority=full_b6_authority)
        db_session.commit()
        persist_runner_report(db_session, execution_id=r1.object_id, new_status="COMPLETED", authority=full_b6_authority)
        db_session.commit()
        execution = db_session.get(RunnerExecution, r1.object_id)
        # No field on RunnerExecution or its decision represents domain
        # validity — structurally impossible to assert one from this model.
        assert not hasattr(execution, "domain_result")
        assert execution.execution_status == "COMPLETED"

    # --- Artifact multiplicity, identity, classification (REQ-B6-018..030) ---

    def test_p11_execution_with_zero_artifacts(self, db_session, full_b6_authority):
        contact = _contact(db_session)
        asset = _asset(db_session)
        case = _case(db_session, contact, asset)
        db_session.commit()
        r1 = admit_execution(db_session, case_id=case.case_id, asset_id=asset.asset_id, runner_type="VIR",
                              runner_version="1.0", authority=full_b6_authority)
        db_session.commit()
        transition_status(db_session, execution_id=r1.object_id, new_status="RUNNING", authority=full_b6_authority)
        db_session.commit()
        persist_runner_report(db_session, execution_id=r1.object_id, new_status="COMPLETED", authority=full_b6_authority)
        db_session.commit()
        execution = db_session.get(RunnerExecution, r1.object_id)
        assert execution.execution_status == "COMPLETED"
        artifacts = db_session.query(RunnerArtifact).filter(RunnerArtifact.execution_id == r1.object_id).all()
        assert len(artifacts) == 0  # valid, non-anomalous (REQ-B6-023 a-ii)

    def test_p12_execution_with_multiple_artifacts(self, db_session, full_b6_authority):
        contact = _contact(db_session)
        asset = _asset(db_session)
        case = _case(db_session, contact, asset)
        db_session.commit()
        _schema_def(db_session)
        r1 = admit_execution(db_session, case_id=case.case_id, asset_id=asset.asset_id, runner_type="VIR",
                              runner_version="1.0", authority=full_b6_authority)
        db_session.commit()

        a1 = register_artifact(
            db_session, execution_id=r1.object_id, artifact_type="vin_result", schema_name="vir.identity.v1",
            schema_version="1", payload={"vin": "1HGCM82633A004352", "confidence": 0.98},
            semantic_function="DOMAIN_DETERMINATION_CARRIER", lifecycle_role="FINAL",
            presentation_role="INTERNAL", authority=full_b6_authority,
        )
        db_session.commit()
        a2 = register_artifact(
            db_session, execution_id=r1.object_id, artifact_type="vin_evidence", schema_name="vir.identity.v1",
            schema_version="1", payload={"vin": "1HGCM82633A004352", "confidence": 0.5},
            semantic_function="EXECUTION_EVIDENCE_CARRIER", lifecycle_role="INTERMEDIATE",
            presentation_role="INTERNAL", authority=full_b6_authority,
        )
        db_session.commit()
        assert a1.outcome == RunnerOutcome.SUCCESS
        assert a2.outcome == RunnerOutcome.SUCCESS
        assert a1.object_id != a2.object_id
        artifacts = db_session.query(RunnerArtifact).filter(RunnerArtifact.execution_id == r1.object_id).all()
        assert len(artifacts) == 2

    def test_p13_artifact_identity_independent_of_payload(self, db_session, full_b6_authority):
        contact = _contact(db_session)
        asset = _asset(db_session)
        case = _case(db_session, contact, asset)
        db_session.commit()
        _schema_def(db_session)
        r1 = admit_execution(db_session, case_id=case.case_id, asset_id=asset.asset_id, runner_type="VIR",
                              runner_version="1.0", authority=full_b6_authority)
        db_session.commit()
        same_payload = {"vin": "1HGCM82633A004352", "confidence": 0.9}
        a1 = register_artifact(db_session, execution_id=r1.object_id, artifact_type="vin_result",
                                schema_name="vir.identity.v1", schema_version="1", payload=same_payload,
                                semantic_function="DOMAIN_DETERMINATION_CARRIER", lifecycle_role="FINAL",
                                presentation_role="INTERNAL", authority=full_b6_authority)
        db_session.commit()
        a2 = register_artifact(db_session, execution_id=r1.object_id, artifact_type="vin_result",
                                schema_name="vir.identity.v1", schema_version="1", payload=same_payload,
                                semantic_function="DOMAIN_DETERMINATION_CARRIER", lifecycle_role="FINAL",
                                presentation_role="INTERNAL", authority=full_b6_authority)
        db_session.commit()
        assert a1.object_id != a2.object_id  # same execution, same payload -> still distinct identity

    def test_p14_structural_validation_reaches_validated(self, db_session, full_b6_authority):
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
                                    payload={"vin": "1HGCM82633A004352", "confidence": 0.98},
                                    semantic_function="DOMAIN_DETERMINATION_CARRIER", lifecycle_role="FINAL",
                                    presentation_role="INTERNAL", authority=full_b6_authority)
        db_session.commit()
        artifact = db_session.get(RunnerArtifact, result.object_id)
        assert artifact.artifact_status == "VALIDATED"

    # --- Supersession consistency (REQ-B6-057, repaired) ---

    def test_p15_supersession_is_coordinated_and_consistent(self, db_session, full_b6_authority):
        contact = _contact(db_session)
        asset = _asset(db_session)
        case = _case(db_session, contact, asset)
        db_session.commit()
        _schema_def(db_session)
        r1 = admit_execution(db_session, case_id=case.case_id, asset_id=asset.asset_id, runner_type="VIR",
                              runner_version="1.0", authority=full_b6_authority)
        db_session.commit()
        original = register_artifact(db_session, execution_id=r1.object_id, artifact_type="vin_result",
                                      schema_name="vir.identity.v1", schema_version="1",
                                      payload={"vin": "1HGCM82633A004352", "confidence": 0.6},
                                      semantic_function="DOMAIN_DETERMINATION_CARRIER", lifecycle_role="FINAL",
                                      presentation_role="INTERNAL", authority=full_b6_authority)
        db_session.commit()
        assert db_session.get(RunnerArtifact, original.object_id).artifact_status == "VALIDATED"

        superseding = supersede_artifact(db_session, old_artifact_id=original.object_id,
                                          new_payload={"vin": "1HGCM82633A004352", "confidence": 0.99},
                                          authority=full_b6_authority)
        db_session.commit()
        assert superseding.outcome == RunnerOutcome.SUCCESS

        old_artifact = db_session.get(RunnerArtifact, original.object_id)
        new_artifact = db_session.get(RunnerArtifact, superseding.object_id)
        assert old_artifact.artifact_status == "SUPERSEDED"
        assert new_artifact.supersedes_artifact_id == original.object_id
        assert old_artifact.artifact_id != new_artifact.artifact_id  # identity stable, not reused

        mismatches = check_supersession_consistency(db_session)
        assert mismatches == []  # REQ-B6-057's zero-mismatch consistency query

    def test_p16_superseded_artifact_retained_not_deleted(self, db_session, full_b6_authority):
        contact = _contact(db_session)
        asset = _asset(db_session)
        case = _case(db_session, contact, asset)
        db_session.commit()
        _schema_def(db_session)
        r1 = admit_execution(db_session, case_id=case.case_id, asset_id=asset.asset_id, runner_type="VIR",
                              runner_version="1.0", authority=full_b6_authority)
        db_session.commit()
        original = register_artifact(db_session, execution_id=r1.object_id, artifact_type="vin_result",
                                      schema_name="vir.identity.v1", schema_version="1",
                                      payload={"vin": "1HGCM82633A004352", "confidence": 0.6},
                                      semantic_function="DOMAIN_DETERMINATION_CARRIER", lifecycle_role="FINAL",
                                      presentation_role="INTERNAL", authority=full_b6_authority)
        db_session.commit()
        supersede_artifact(db_session, old_artifact_id=original.object_id,
                            new_payload={"vin": "1HGCM82633A004352", "confidence": 0.99}, authority=full_b6_authority)
        db_session.commit()
        assert db_session.get(RunnerArtifact, original.object_id) is not None  # never deleted

    # --- Correction / history (REQ-B6-062..065) ---

    def test_p17_metadata_correction_is_append_only_and_reconstructable(self, db_session, full_b6_authority):
        contact = _contact(db_session)
        asset = _asset(db_session)
        case = _case(db_session, contact, asset)
        db_session.commit()
        r1 = admit_execution(db_session, case_id=case.case_id, asset_id=asset.asset_id, runner_type="VIR",
                              runner_version="1.0", execution_purpose="original purpose", authority=full_b6_authority)
        db_session.commit()

        result = correct_execution_metadata(db_session, execution_id=r1.object_id, field_name="execution_purpose",
                                             new_value="corrected purpose", authority=full_b6_authority)
        db_session.commit()
        assert result.outcome == RunnerOutcome.SUCCESS
        execution = db_session.get(RunnerExecution, r1.object_id)
        assert execution.execution_purpose == "corrected purpose"

        original_value = reconstruct_original_value(db_session, execution_id=r1.object_id, field_name="execution_purpose")
        assert original_value == "original purpose"  # REQ-B6-065: history reconstructable

    def test_p19_content_hash_computed_and_matches(self, db_session, full_b6_authority):
        """REQ-B6-053/054: hash required for inline content, computed over
        the exact persisted payload."""
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
                                    payload={"vin": "1HGCM82633A004352", "confidence": 0.98},
                                    semantic_function="DOMAIN_DETERMINATION_CARRIER", lifecycle_role="FINAL",
                                    presentation_role="INTERNAL", authority=full_b6_authority)
        db_session.commit()
        artifact = db_session.get(RunnerArtifact, result.object_id)
        assert artifact.content_hash is not None
        assert artifact.hash_algorithm is not None

        from app.cpl.runners.artifacts import verify_content_integrity, IntegrityCheckOutcome
        assert verify_content_integrity(artifact) == IntegrityCheckOutcome.MATCH

    def test_p20_integrity_mismatch_detected_and_distinct_from_rejected(self, db_session, full_b6_authority):
        """REQ-B6-055/056: a mismatch is flagged distinctly, not silently
        corrected and not conflated with structural REJECTED."""
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
                                    payload={"vin": "1HGCM82633A004352", "confidence": 0.98},
                                    semantic_function="DOMAIN_DETERMINATION_CARRIER", lifecycle_role="FINAL",
                                    presentation_role="INTERNAL", authority=full_b6_authority)
        db_session.commit()
        artifact = db_session.get(RunnerArtifact, result.object_id)
        status_before = artifact.artifact_status
        artifact.payload = {"vin": "TAMPERED", "confidence": 0.98}  # simulate corruption, never done by real code

        from app.cpl.runners.artifacts import verify_content_integrity, IntegrityCheckOutcome
        assert verify_content_integrity(artifact) == IntegrityCheckOutcome.MISMATCH
        assert artifact.artifact_status == status_before  # not silently corrected or reclassified as REJECTED

    def test_p21_blocked_transition_and_recovery(self, db_session, full_b6_authority):
        """REQ-B6-012: BLOCKED is a valid pre-terminal state reachable
        from CREATED/QUEUED/RUNNING and recoverable back to RUNNING."""
        contact = _contact(db_session)
        asset = _asset(db_session)
        case = _case(db_session, contact, asset)
        db_session.commit()
        r1 = admit_execution(db_session, case_id=case.case_id, asset_id=asset.asset_id, runner_type="VIR",
                              runner_version="1.0", authority=full_b6_authority)
        db_session.commit()
        transition_status(db_session, execution_id=r1.object_id, new_status="RUNNING", authority=full_b6_authority)
        db_session.commit()
        r2 = transition_status(db_session, execution_id=r1.object_id, new_status="BLOCKED", authority=full_b6_authority)
        db_session.commit()
        assert r2.outcome == RunnerOutcome.SUCCESS
        assert db_session.get(RunnerExecution, r1.object_id).execution_status == "BLOCKED"

        r3 = transition_status(db_session, execution_id=r1.object_id, new_status="RUNNING", authority=full_b6_authority)
        db_session.commit()
        assert r3.outcome == RunnerOutcome.SUCCESS
        assert db_session.get(RunnerExecution, r1.object_id).execution_status == "RUNNING"
        """REQ-B6-063 category C: a genuinely new attempt is always a NEW
        RunnerExecution, never expressed as a correction of the prior one."""
        contact = _contact(db_session)
        asset = _asset(db_session)
        case = _case(db_session, contact, asset)
        db_session.commit()
        r1 = admit_execution(db_session, case_id=case.case_id, asset_id=asset.asset_id, runner_type="VIR",
                              runner_version="1.0", authority=full_b6_authority)
        db_session.commit()
        r2 = retry_execution(db_session, case_id=case.case_id, asset_id=asset.asset_id, runner_type="VIR",
                              runner_version="1.0", authority=full_b6_authority)
        db_session.commit()
        assert r2.object_id != r1.object_id
        from app.cpl.models.runner_execution_correction import RunnerExecutionCorrection
        corrections = db_session.query(RunnerExecutionCorrection).filter(RunnerExecutionCorrection.execution_id == r1.object_id).count()
        assert corrections == 0  # retry never recorded as a correction of r1
