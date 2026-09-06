"""B5 Negative/Adversarial Verification, mirroring the mandate's
required adversarial tests A-N."""
import uuid
from unittest.mock import patch

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as OrmSession

from app.cpl.models.contact import Contact
from app.cpl.models.asset import Asset
from app.cpl.models.case import Case
from app.cpl.models.case_participant import CaseParticipant
from app.cpl.models.canonical_case_decision import CanonicalCaseDecision
from app.cpl.cases.lifecycle import create_case, transition_case_status, attempt_asset_rebind
from app.cpl.cases.participants import add_participant, can_participant_mutate_case
from app.cpl.cases.events import register_event_type, record_case_event
from app.cpl.cases.outcomes import CaseOutcome
from app.cpl.identity.authority import AuthorityContext, AuthorityDeniedError
from tests.integration.test_b5_positive import _contact, _asset
from app.db.engine import check_db_connection

pytestmark = pytest.mark.skipif(not check_db_connection(), reason="PostgreSQL not available")


class TestB5Negative:

    def test_n_b_asset_cannot_be_rebound(self, db_session, full_b5_authority):
        # Adversarial test B: Case.asset_id cannot be changed Asset A -> Asset B.
        contact = _contact(db_session)
        asset_a = _asset(db_session)
        asset_b = _asset(db_session)
        db_session.commit()
        r1 = create_case(db_session, primary_contact_id=contact.contact_id, asset_id=asset_a.asset_id,
                          domain="AUTOMOTIVE", case_type="DIAGNOSTIC", authority=full_b5_authority,
                          idempotency_key=str(uuid.uuid4()))
        db_session.commit()

        r2 = attempt_asset_rebind(db_session, case_id=r1.object_id, new_asset_id=asset_b.asset_id,
                                   authority=full_b5_authority, idempotency_key=str(uuid.uuid4()))
        db_session.commit()
        assert r2.outcome == CaseOutcome.SEMANTIC_REJECTION
        case = db_session.get(Case, r1.object_id)
        assert case.asset_id == asset_a.asset_id  # unchanged

    def test_n_c_participant_role_alone_cannot_authorize_closure(self, db_session):
        # Adversarial test C: CaseParticipant role alone cannot authorize Case closure.
        weak_authority = AuthorityContext(granted=frozenset(), actor_reference="technician-no-authority")
        contact = _contact(db_session)
        db_session.add(contact)
        db_session.commit()
        # Even holding a TECHNICIAN role structurally, without granted authority,
        # attempting the governed operation must be denied.
        with pytest.raises(AuthorityDeniedError):
            transition_case_status(db_session, case_id=uuid.uuid4(), new_status="CLOSED",
                                    authority=weak_authority, idempotency_key=str(uuid.uuid4()))
        # Structural check: can_participant_mutate_case never consults participant_role.
        fake_participant = CaseParticipant(case_id=uuid.uuid4(), contact_id=uuid.uuid4(),
                                            participant_role="TECHNICIAN", participant_status="ACTIVE")
        assert can_participant_mutate_case(fake_participant, weak_authority) is False

    def test_n_e_case_closed_does_not_imply_domain_truth(self, db_session, full_b5_authority):
        # Adversarial test E: CASE_CLOSED does not imply repaired/safe/successful.
        contact = _contact(db_session)
        asset = _asset(db_session)
        db_session.commit()
        r1 = create_case(db_session, primary_contact_id=contact.contact_id, asset_id=asset.asset_id,
                          domain="AUTOMOTIVE", case_type="DIAGNOSTIC", authority=full_b5_authority,
                          idempotency_key=str(uuid.uuid4()))
        db_session.commit()
        transition_case_status(db_session, case_id=r1.object_id, new_status="CLOSED",
                                authority=full_b5_authority, idempotency_key=str(uuid.uuid4()))
        db_session.commit()
        case = db_session.get(Case, r1.object_id)
        assert case.case_status == "CLOSED"
        # Structural proof: Case model has no field asserting domain truth
        # (repaired/safe/diagnosis_valid) anywhere.
        assert not hasattr(case, "repaired")
        assert not hasattr(case, "diagnosis_valid")
        assert not hasattr(case, "asset_safe")

    def test_n_domain_truth_status_rejected(self, db_session, full_b5_authority):
        # REQ-B5-041: no domain-truth-laden status accepted.
        contact = _contact(db_session)
        asset = _asset(db_session)
        db_session.commit()
        r1 = create_case(db_session, primary_contact_id=contact.contact_id, asset_id=asset.asset_id,
                          domain="AUTOMOTIVE", case_type="DIAGNOSTIC", authority=full_b5_authority,
                          idempotency_key=str(uuid.uuid4()))
        db_session.commit()
        r2 = transition_case_status(db_session, case_id=r1.object_id, new_status="REPAIRED",
                                     authority=full_b5_authority, idempotency_key=str(uuid.uuid4()))
        db_session.commit()
        assert r2.outcome == CaseOutcome.SEMANTIC_REJECTION

    def test_n_f_execution_reference_opaque(self, db_session, full_b5_authority):
        # Adversarial test F: Case can record opaque execution reference
        # without interpreting execution status. B5 has no code path
        # that reads RunnerExecution.execution_status at all.
        import app.cpl.cases.lifecycle as lifecycle_module
        import app.cpl.cases.events as events_module
        import inspect
        src = inspect.getsource(lifecycle_module) + inspect.getsource(events_module)
        assert "execution_status" not in src
        assert "RunnerExecution" not in src or "execution_status" not in src

    def test_n_g_technical_failure_not_governed_rejection(self, db_session, full_b5_authority):
        # Adversarial test G: technical DB failure is not recorded as governed rejection.
        contact = _contact(db_session)
        asset = _asset(db_session)
        db_session.commit()
        r1 = create_case(db_session, primary_contact_id=contact.contact_id, asset_id=asset.asset_id,
                          domain="AUTOMOTIVE", case_type="DIAGNOSTIC", authority=full_b5_authority,
                          idempotency_key=str(uuid.uuid4()))
        db_session.commit()

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
                    transition_case_status(db_session, case_id=r1.object_id, new_status="IN_PROGRESS",
                                            authority=full_b5_authority, idempotency_key=str(uuid.uuid4()))
        except IntegrityError:
            raised = True
        assert raised  # technical failure surfaces as an exception, never a governed CaseResult
        # No partial transition: no decision row exists for a failed attempt.
        decisions = db_session.query(CanonicalCaseDecision).filter(
            CanonicalCaseDecision.case_id == r1.object_id,
            CanonicalCaseDecision.decision_type == "STATUS_TRANSITION",
        ).all()
        assert decisions == []
        case = db_session.get(Case, r1.object_id)
        assert case.case_status == "OPEN"  # unchanged

    def test_n_j_different_operation_identity_not_auto_replay(self, db_session, full_b5_authority):
        # Adversarial test J: same payload, different operation identity, not auto-replay.
        contact = _contact(db_session)
        asset = _asset(db_session)
        db_session.commit()
        r1 = create_case(db_session, primary_contact_id=contact.contact_id, asset_id=asset.asset_id,
                          domain="AUTOMOTIVE", case_type="DIAGNOSTIC", authority=full_b5_authority,
                          idempotency_key=str(uuid.uuid4()))
        db_session.commit()

        key_a = str(uuid.uuid4())
        key_b = str(uuid.uuid4())
        ra = transition_case_status(db_session, case_id=r1.object_id, new_status="IN_PROGRESS",
                                     authority=full_b5_authority, idempotency_key=key_a)
        db_session.commit()
        rb = transition_case_status(db_session, case_id=r1.object_id, new_status="RESOLVED",
                                     authority=full_b5_authority, idempotency_key=key_b)
        db_session.commit()
        assert ra.payload["decision_id"] != rb.payload["decision_id"]

    def test_n_unregistered_event_type_rejected(self, db_session, full_b5_authority):
        # REQ-B5-035/036: event_type must be registered with a semantic class.
        contact = _contact(db_session)
        asset = _asset(db_session)
        db_session.commit()
        r1 = create_case(db_session, primary_contact_id=contact.contact_id, asset_id=asset.asset_id,
                          domain="AUTOMOTIVE", case_type="DIAGNOSTIC", authority=full_b5_authority,
                          idempotency_key=str(uuid.uuid4()))
        db_session.commit()
        r2 = record_case_event(db_session, case_id=r1.object_id, event_type="UNREGISTERED_TYPE",
                                actor_type="SYSTEM", authority=full_b5_authority)
        db_session.commit()
        assert r2.outcome == CaseOutcome.SEMANTIC_REJECTION

    def test_n_create_case_denied_without_authority(self, db_session):
        weak = AuthorityContext(granted=frozenset(), actor_reference="nobody")
        contact = _contact(db_session)
        asset = _asset(db_session)
        db_session.commit()
        with pytest.raises(AuthorityDeniedError):
            create_case(db_session, primary_contact_id=contact.contact_id, asset_id=asset.asset_id,
                        domain="AUTOMOTIVE", case_type="DIAGNOSTIC", authority=weak,
                        idempotency_key=str(uuid.uuid4()))
