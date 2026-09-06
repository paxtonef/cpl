"""R7: dedicated create_case() pipeline-ordering test suite.

Verifies genuine decision-before-effect for CREATE (not merely final
transactional atomicity), using the deferred FK on
CanonicalCaseDecision.case_id."""
import uuid
from unittest.mock import patch

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as OrmSession

from app.cpl.models.case import Case
from app.cpl.models.canonical_case_decision import CanonicalCaseDecision
from app.cpl.cases.lifecycle import create_case
from app.cpl.cases.outcomes import CaseOutcome
from tests.integration.test_b5_positive import _contact, _asset
from app.db.engine import check_db_connection

pytestmark = pytest.mark.skipif(not check_db_connection(), reason="PostgreSQL not available")


class TestR7CreateCasePipelineOrdering:

    def test_1_authority_succeeds_precondition(self, db_session, full_b5_authority):
        # Sanity precondition for the rest of this suite.
        contact = _contact(db_session)
        asset = _asset(db_session)
        db_session.commit()
        r = create_case(db_session, primary_contact_id=contact.contact_id, asset_id=asset.asset_id,
                         domain="AUTOMOTIVE", case_type="DIAGNOSTIC", authority=full_b5_authority,
                         idempotency_key=str(uuid.uuid4()))
        db_session.commit()
        assert r.outcome == CaseOutcome.SUCCESS

    def test_2_decision_insert_precedes_case_insert_in_execution_order(self, db_session, full_b5_authority):
        # Proves ORDER, not just atomicity: instrument session.flush to
        # record which table each flush actually touches, in sequence.
        contact = _contact(db_session)
        asset = _asset(db_session)
        db_session.commit()

        flush_log = []
        original_flush = OrmSession.flush

        def logging_flush(self, *args, **kwargs):
            # Inspect pending new objects before they are cleared by flush.
            pending_types = {type(obj).__name__ for obj in self.new}
            result = original_flush(self, *args, **kwargs)
            if pending_types:
                flush_log.append(pending_types)
            return result

        with patch.object(OrmSession, "flush", logging_flush):
            r = create_case(db_session, primary_contact_id=contact.contact_id, asset_id=asset.asset_id,
                             domain="AUTOMOTIVE", case_type="DIAGNOSTIC", authority=full_b5_authority,
                             idempotency_key=str(uuid.uuid4()))
        db_session.commit()
        assert r.outcome == CaseOutcome.SUCCESS

        # The decision INSERT must appear in the flush log strictly
        # before the Case INSERT.
        decision_flush_index = next(i for i, s in enumerate(flush_log) if "CanonicalCaseDecision" in s)
        case_flush_index = next(i for i, s in enumerate(flush_log) if "Case" in s and "CanonicalCaseDecision" not in s)
        assert decision_flush_index < case_flush_index, (
            f"decision flush ({decision_flush_index}) must precede Case flush ({case_flush_index}), "
            f"flush_log={flush_log}"
        )

    def test_3_failure_at_decision_establishment_produces_no_case(self, db_session, full_b5_authority):
        contact = _contact(db_session)
        asset = _asset(db_session)
        db_session.commit()

        original_flush = OrmSession.flush
        call_count = {"n": 0}

        def failing_flush(self, *args, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 1:  # the very first flush is the decision
                raise IntegrityError("simulated failure at decision stage", None, None)
            return original_flush(self, *args, **kwargs)

        raised = False
        try:
            with db_session.begin_nested():
                with patch.object(OrmSession, "flush", failing_flush):
                    create_case(db_session, primary_contact_id=contact.contact_id, asset_id=asset.asset_id,
                                domain="AUTOMOTIVE", case_type="DIAGNOSTIC", authority=full_b5_authority,
                                idempotency_key=str(uuid.uuid4()))
        except IntegrityError:
            raised = True
        assert raised
        cases = db_session.query(Case).filter(Case.primary_contact_id == contact.contact_id).all()
        assert cases == []  # no Case, since decision (which precedes it) never completed

    def test_4_failure_during_case_effect_produces_no_committed_decision_or_case(self, db_session, full_b5_authority):
        contact = _contact(db_session)
        asset = _asset(db_session)
        db_session.commit()

        original_flush = OrmSession.flush
        call_count = {"n": 0}

        def failing_flush(self, *args, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 2:  # decision flush = 1 (succeeds), Case flush = 2 (fails)
                raise IntegrityError("simulated failure at Case effect stage", None, None)
            return original_flush(self, *args, **kwargs)

        raised = False
        try:
            with db_session.begin_nested():
                with patch.object(OrmSession, "flush", failing_flush):
                    create_case(db_session, primary_contact_id=contact.contact_id, asset_id=asset.asset_id,
                                domain="AUTOMOTIVE", case_type="DIAGNOSTIC", authority=full_b5_authority,
                                idempotency_key=str(uuid.uuid4()))
        except IntegrityError:
            raised = True
        assert raised
        # Even though the decision row was successfully flushed to the
        # open transaction BEFORE the Case failure, the whole nested
        # transaction rolls back on exception, so neither the deferred-FK
        # decision nor the Case survives. Deferred-checking only delays
        # WHEN the FK is validated (until commit) — it does not create a
        # committed, orphaned decision.
        decisions = db_session.query(CanonicalCaseDecision).filter(
            CanonicalCaseDecision.decision_type == "CREATE",
        ).all()
        cases = db_session.query(Case).filter(Case.primary_contact_id == contact.contact_id).all()
        assert decisions == []
        assert cases == []

    def test_5_successful_operation_produces_exactly_one_case_and_one_decision(self, db_session, full_b5_authority):
        contact = _contact(db_session)
        asset = _asset(db_session)
        db_session.commit()
        r = create_case(db_session, primary_contact_id=contact.contact_id, asset_id=asset.asset_id,
                         domain="AUTOMOTIVE", case_type="DIAGNOSTIC", authority=full_b5_authority,
                         idempotency_key=str(uuid.uuid4()))
        db_session.commit()
        cases = db_session.query(Case).filter(Case.case_id == r.object_id).all()
        decisions = db_session.query(CanonicalCaseDecision).filter(
            CanonicalCaseDecision.case_id == r.object_id, CanonicalCaseDecision.decision_type == "CREATE",
        ).all()
        assert len(cases) == 1
        assert len(decisions) == 1
        assert decisions[0].result_object_id == r.object_id

    def test_6_replay_produces_no_second_case_or_decision(self, db_session, full_b5_authority):
        contact = _contact(db_session)
        asset = _asset(db_session)
        db_session.commit()
        key = str(uuid.uuid4())
        r1 = create_case(db_session, primary_contact_id=contact.contact_id, asset_id=asset.asset_id,
                          domain="AUTOMOTIVE", case_type="DIAGNOSTIC", authority=full_b5_authority,
                          idempotency_key=key)
        db_session.commit()
        r2 = create_case(db_session, primary_contact_id=contact.contact_id, asset_id=asset.asset_id,
                          domain="AUTOMOTIVE", case_type="DIAGNOSTIC", authority=full_b5_authority,
                          idempotency_key=key)
        db_session.commit()

        assert r1.object_id == r2.object_id  # original Case identity returned
        assert r2.payload.get("replay") is True
        cases = db_session.query(Case).filter(Case.primary_contact_id == contact.contact_id).all()
        decisions = db_session.query(CanonicalCaseDecision).filter(
            CanonicalCaseDecision.decision_type == "CREATE", CanonicalCaseDecision.case_id == r1.object_id,
        ).all()
        assert len(cases) == 1
        assert len(decisions) == 1
