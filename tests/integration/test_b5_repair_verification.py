"""B5 WIP checkpoint repair verification: R1 (decision-before-effect),
R2 (idempotent replay outcome fidelity), R3 (failure category
operationalization), R4 (real RunnerExecution boundary test)."""
import uuid
from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as OrmSession

from app.cpl.models.case import Case
from app.cpl.models.case_participant import CaseParticipant
from app.cpl.models.case_event import CaseEvent
from app.cpl.models.canonical_case_decision import CanonicalCaseDecision
from app.cpl.models.runner_execution import RunnerExecution
from app.cpl.cases.lifecycle import create_case, transition_case_status, attempt_asset_rebind
from app.cpl.cases.participants import add_participant, remove_participant
from app.cpl.cases.events import register_event_type, record_case_event, correct_case_event
from app.cpl.cases.correction import correct_case_metadata
from app.cpl.cases.outcomes import CaseOutcome
from app.cpl.identity.authority import AuthorityContext, AuthorityDeniedError
from tests.integration.test_b5_positive import _contact, _asset
from app.db.engine import check_db_connection

pytestmark = pytest.mark.skipif(not check_db_connection(), reason="PostgreSQL not available")


def _make_case(session, authority):
    contact = _contact(session)
    asset = _asset(session)
    session.commit()
    r = create_case(session, primary_contact_id=contact.contact_id, asset_id=asset.asset_id,
                     domain="AUTOMOTIVE", case_type="DIAGNOSTIC", authority=authority,
                     idempotency_key=str(uuid.uuid4()))
    session.commit()
    return r.object_id


class TestR1DecisionBeforeEffect:

    def test_add_participant_decision_before_effect(self, db_session, full_b5_authority):
        case_id = _make_case(db_session, full_b5_authority)
        technician = _contact(db_session, "Tech")
        db_session.commit()

        original_flush = OrmSession.flush
        call_count = {"n": 0}

        def failing_flush(self, *args, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 2:
                raise IntegrityError("simulated failure", None, None)
            return original_flush(self, *args, **kwargs)

        raised = False
        try:
            with db_session.begin_nested():
                with patch.object(OrmSession, "flush", failing_flush):
                    add_participant(db_session, case_id=case_id, contact_id=technician.contact_id,
                                     participant_role="TECHNICIAN", authority=full_b5_authority,
                                     idempotency_key=str(uuid.uuid4()))
        except IntegrityError:
            raised = True
        assert raised
        decisions = db_session.query(CanonicalCaseDecision).filter(
            CanonicalCaseDecision.case_id == case_id, CanonicalCaseDecision.decision_type == "PARTICIPANT_ADD",
        ).all()
        assert decisions == []
        participants = db_session.query(CaseParticipant).filter(CaseParticipant.case_id == case_id).all()
        assert participants == []

    def test_correct_case_event_decision_before_effect(self, db_session, full_b5_authority):
        case_id = _make_case(db_session, full_b5_authority)
        register_event_type(db_session, event_type="DIAGNOSIS_REPORTED", semantic_class="DOMAIN_ASSERTION")
        db_session.commit()
        r = record_case_event(db_session, case_id=case_id, event_type="DIAGNOSIS_REPORTED",
                               actor_type="RUNNER", payload={"finding": "original"}, authority=full_b5_authority)
        db_session.commit()

        original_flush = OrmSession.flush
        call_count = {"n": 0}

        def failing_flush(self, *args, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 2:
                raise IntegrityError("simulated failure", None, None)
            return original_flush(self, *args, **kwargs)

        raised = False
        try:
            with db_session.begin_nested():
                with patch.object(OrmSession, "flush", failing_flush):
                    correct_case_event(db_session, event_id_to_correct=r.object_id,
                                        corrected_payload={"finding": "corrected"}, reason="test",
                                        authority=full_b5_authority, idempotency_key=str(uuid.uuid4()))
        except IntegrityError:
            raised = True
        assert raised
        original = db_session.get(CaseEvent, r.object_id)
        assert original.event_status == "CURRENT"
        decisions = db_session.query(CanonicalCaseDecision).filter(
            CanonicalCaseDecision.decision_type == "EVENT_CORRECTION",
        ).all()
        assert decisions == []


class TestR2ReplayOutcomeFidelity:

    def test_add_participant_replay_object_id(self, db_session, full_b5_authority):
        case_id = _make_case(db_session, full_b5_authority)
        technician = _contact(db_session, "Tech2")
        db_session.commit()
        key = str(uuid.uuid4())
        r1 = add_participant(db_session, case_id=case_id, contact_id=technician.contact_id,
                              participant_role="TECHNICIAN", authority=full_b5_authority, idempotency_key=key)
        db_session.commit()
        r2 = add_participant(db_session, case_id=case_id, contact_id=technician.contact_id,
                              participant_role="TECHNICIAN", authority=full_b5_authority, idempotency_key=key)
        db_session.commit()
        assert r1.object_id == r2.object_id
        assert r2.payload.get("replay") is True
        assert r2.object_id != case_id

    def test_remove_participant_replay_object_id(self, db_session, full_b5_authority):
        case_id = _make_case(db_session, full_b5_authority)
        technician = _contact(db_session, "Tech3")
        db_session.commit()
        r1 = add_participant(db_session, case_id=case_id, contact_id=technician.contact_id,
                              participant_role="TECHNICIAN", authority=full_b5_authority,
                              idempotency_key=str(uuid.uuid4()))
        db_session.commit()
        key = str(uuid.uuid4())
        r2 = remove_participant(db_session, case_participant_id=r1.object_id, authority=full_b5_authority,
                                 idempotency_key=key)
        db_session.commit()
        r3 = remove_participant(db_session, case_participant_id=r1.object_id, authority=full_b5_authority,
                                 idempotency_key=key)
        db_session.commit()
        assert r2.object_id == r3.object_id == r1.object_id

    def test_event_correction_replay_object_id(self, db_session, full_b5_authority):
        case_id = _make_case(db_session, full_b5_authority)
        register_event_type(db_session, event_type="DIAGNOSIS_REPORTED", semantic_class="DOMAIN_ASSERTION")
        db_session.commit()
        r1 = record_case_event(db_session, case_id=case_id, event_type="DIAGNOSIS_REPORTED",
                                actor_type="RUNNER", payload={"finding": "x"}, authority=full_b5_authority)
        db_session.commit()
        key = str(uuid.uuid4())
        r2 = correct_case_event(db_session, event_id_to_correct=r1.object_id, corrected_payload={"finding": "y"},
                                 reason="test", authority=full_b5_authority, idempotency_key=key)
        db_session.commit()
        r3 = correct_case_event(db_session, event_id_to_correct=r1.object_id, corrected_payload={"finding": "y"},
                                 reason="test", authority=full_b5_authority, idempotency_key=key)
        db_session.commit()
        assert r2.object_id == r3.object_id
        assert r3.object_id != case_id
        assert r3.object_id != r1.object_id

    def test_metadata_correction_replay_object_id(self, db_session, full_b5_authority):
        case_id = _make_case(db_session, full_b5_authority)
        key = str(uuid.uuid4())
        r1 = correct_case_metadata(db_session, case_id=case_id, new_title="A", reason="x",
                                    authority=full_b5_authority, idempotency_key=key)
        db_session.commit()
        r2 = correct_case_metadata(db_session, case_id=case_id, new_title="A", reason="x",
                                    authority=full_b5_authority, idempotency_key=key)
        db_session.commit()
        assert r1.object_id == r2.object_id == case_id

    def test_asset_rebind_attempt_replay_consistent(self, db_session, full_b5_authority):
        contact = _contact(db_session)
        asset_a = _asset(db_session)
        asset_b = _asset(db_session)
        db_session.commit()
        r_create = create_case(db_session, primary_contact_id=contact.contact_id, asset_id=asset_a.asset_id,
                                domain="AUTOMOTIVE", case_type="DIAGNOSTIC", authority=full_b5_authority,
                                idempotency_key=str(uuid.uuid4()))
        db_session.commit()
        key = str(uuid.uuid4())
        r1 = attempt_asset_rebind(db_session, case_id=r_create.object_id, new_asset_id=asset_b.asset_id,
                                   authority=full_b5_authority, idempotency_key=key)
        db_session.commit()
        r2 = attempt_asset_rebind(db_session, case_id=r_create.object_id, new_asset_id=asset_b.asset_id,
                                   authority=full_b5_authority, idempotency_key=key)
        db_session.commit()
        assert r1.outcome == r2.outcome == CaseOutcome.SEMANTIC_REJECTION


class TestR3FailureCategories:

    def test_authority_rejection_is_distinguishable_type(self, db_session, full_b5_authority):
        weak = AuthorityContext(granted=frozenset(), actor_reference="nobody")
        contact = _contact(db_session)
        asset = _asset(db_session)
        db_session.commit()
        with pytest.raises(AuthorityDeniedError) as exc_info:
            create_case(db_session, primary_contact_id=contact.contact_id, asset_id=asset.asset_id,
                        domain="AUTOMOTIVE", case_type="DIAGNOSTIC", authority=weak,
                        idempotency_key=str(uuid.uuid4()))
        assert not isinstance(exc_info.value, IntegrityError)

    def test_semantic_rejection_asset_rebind(self, db_session, full_b5_authority):
        case_id = _make_case(db_session, full_b5_authority)
        asset_b = _asset(db_session)
        db_session.commit()
        r = attempt_asset_rebind(db_session, case_id=case_id, new_asset_id=asset_b.asset_id,
                                  authority=full_b5_authority, idempotency_key=str(uuid.uuid4()))
        db_session.commit()
        assert r.outcome == CaseOutcome.SEMANTIC_REJECTION

    def test_unresolved_case_creation_pending_asset_hold(self, db_session, full_b5_authority):
        from app.cpl.models.canonical_asset_identity_decision import CanonicalAssetIdentityDecision
        from app.cpl.models.asset_identity_resolution import AssetIdentityResolution

        contact = _contact(db_session)
        asset_a = _asset(db_session)
        asset_b = _asset(db_session)
        db_session.commit()
        resolution = AssetIdentityResolution(asset_id=asset_a.asset_id, resolver_type="VIR",
                                              resolver_version="1.0", resolution_status="RESOLVED",
                                              canonical_identity_payload={})
        db_session.add(resolution)
        db_session.flush()
        hold_decision = CanonicalAssetIdentityDecision(
            decision_type="MERGE", source_asset_id=asset_a.asset_id, target_asset_id=asset_b.asset_id,
            resolution_id=resolution.resolution_id, result="HOLD",
        )
        db_session.add(hold_decision)
        db_session.commit()

        r = create_case(db_session, primary_contact_id=contact.contact_id, asset_id=asset_a.asset_id,
                         domain="AUTOMOTIVE", case_type="DIAGNOSTIC", authority=full_b5_authority,
                         idempotency_key=str(uuid.uuid4()))
        db_session.commit()
        assert r.outcome == CaseOutcome.UNRESOLVED

    def test_conflict_correction_race(self, db_session, full_b5_authority):
        case_id = _make_case(db_session, full_b5_authority)
        register_event_type(db_session, event_type="DIAGNOSIS_REPORTED", semantic_class="DOMAIN_ASSERTION")
        db_session.commit()
        r1 = record_case_event(db_session, case_id=case_id, event_type="DIAGNOSIS_REPORTED",
                                actor_type="RUNNER", payload={"finding": "x"}, authority=full_b5_authority)
        db_session.commit()
        correct_case_event(db_session, event_id_to_correct=r1.object_id, corrected_payload={"finding": "y"},
                            reason="first correction", authority=full_b5_authority,
                            idempotency_key=str(uuid.uuid4()))
        db_session.commit()
        r2 = correct_case_event(db_session, event_id_to_correct=r1.object_id, corrected_payload={"finding": "z"},
                                 reason="racing correction", authority=full_b5_authority,
                                 idempotency_key=str(uuid.uuid4()))
        db_session.commit()
        assert r2.outcome == CaseOutcome.CONFLICT

    def test_technical_failure_never_governed_rejection(self, db_session, full_b5_authority):
        case_id = _make_case(db_session, full_b5_authority)

        original_flush = OrmSession.flush
        call_count = {"n": 0}

        def failing_flush(self, *args, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 2:
                raise IntegrityError("simulated DB failure", None, None)
            return original_flush(self, *args, **kwargs)

        raised = False
        try:
            with db_session.begin_nested():
                with patch.object(OrmSession, "flush", failing_flush):
                    transition_case_status(db_session, case_id=case_id, new_status="IN_PROGRESS",
                                            authority=full_b5_authority, idempotency_key=str(uuid.uuid4()))
        except IntegrityError:
            raised = True
        assert raised


class TestR4ExecutionReferenceBoundary:

    def test_real_runner_execution_reference_preserved_without_interpretation(self, db_session, full_b5_authority):
        case_id = _make_case(db_session, full_b5_authority)
        asset_id = db_session.get(Case, case_id).asset_id
        execution = RunnerExecution(case_id=case_id, asset_id=asset_id, runner_type="VEHICLE_PGDR",
                                     runner_version="1.0", execution_status="RUNNING")
        db_session.add(execution)
        db_session.flush()

        register_event_type(db_session, event_type="DIAGNOSIS_REPORTED", semantic_class="DOMAIN_ASSERTION")
        db_session.commit()

        case = db_session.get(Case, case_id)
        case.current_execution_id = execution.execution_id
        db_session.commit()

        r = record_case_event(db_session, case_id=case_id, event_type="DIAGNOSIS_REPORTED",
                               actor_type="RUNNER", execution_id=execution.execution_id,
                               payload={"finding": "test"}, authority=full_b5_authority)
        db_session.commit()
        event = db_session.get(CaseEvent, r.object_id)
        assert event.execution_id == execution.execution_id

        for status in ("COMPLETED", "FAILED", "BLOCKED"):
            execution.execution_status = status
            if status == "COMPLETED":
                execution.completed_at = datetime.now(timezone.utc)
            db_session.commit()
            case = db_session.get(Case, case_id)
            assert case.case_status == "OPEN"
            assert case.current_execution_id == execution.execution_id
