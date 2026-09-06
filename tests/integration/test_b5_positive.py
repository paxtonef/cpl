"""B5 Positive Verification. Traces to REQ-B5-* per B5_CASE_GOVERNANCE_REQUIREMENT_MATRIX_v0.2.md."""
import uuid
from datetime import datetime, timezone, timedelta

import pytest

from app.cpl.models.contact import Contact
from app.cpl.models.asset import Asset
from app.cpl.models.case import Case
from app.cpl.models.case_event import CaseEvent
from app.cpl.models.canonical_case_decision import CanonicalCaseDecision
from app.cpl.cases.lifecycle import create_case, transition_case_status, attempt_asset_rebind
from app.cpl.cases.participants import add_participant, remove_participant
from app.cpl.cases.events import register_event_type, record_case_event, correct_case_event
from app.cpl.cases.correction import correct_case_metadata
from app.cpl.cases.outcomes import CaseOutcome
from app.db.engine import check_db_connection

pytestmark = pytest.mark.skipif(not check_db_connection(), reason="PostgreSQL not available")


def _contact(session, name="Test Contact"):
    c = Contact(contact_type="PERSON", display_name=name)
    session.add(c)
    session.flush()
    return c


def _asset(session):
    a = Asset(asset_domain="AUTOMOTIVE", asset_type="PASSENGER_CAR", asset_status="ACTIVE")
    session.add(a)
    session.flush()
    return a


class TestB5Positive:

    def test_p01_create_case(self, db_session, full_b5_authority):
        contact = _contact(db_session)
        asset = _asset(db_session)
        db_session.commit()

        result = create_case(db_session, primary_contact_id=contact.contact_id, asset_id=asset.asset_id,
                              domain="AUTOMOTIVE", case_type="DIAGNOSTIC", title="Engine noise",
                              authority=full_b5_authority, idempotency_key=str(uuid.uuid4()))
        db_session.commit()
        assert result.outcome == CaseOutcome.SUCCESS
        case = db_session.get(Case, result.object_id)
        assert case.case_status == "OPEN"

    def test_p02_case_identity_stable_across_status_change(self, db_session, full_b5_authority):
        contact = _contact(db_session)
        asset = _asset(db_session)
        db_session.commit()
        r1 = create_case(db_session, primary_contact_id=contact.contact_id, asset_id=asset.asset_id,
                          domain="AUTOMOTIVE", case_type="DIAGNOSTIC", authority=full_b5_authority,
                          idempotency_key=str(uuid.uuid4()))
        db_session.commit()
        case_id_before = r1.object_id

        r2 = transition_case_status(db_session, case_id=case_id_before, new_status="IN_PROGRESS",
                                     authority=full_b5_authority, idempotency_key=str(uuid.uuid4()))
        db_session.commit()
        assert r2.outcome == CaseOutcome.SUCCESS
        assert r2.object_id == case_id_before  # REQ-B5-004: identity stable across status change

    def test_p03_status_transition_records_decision(self, db_session, full_b5_authority):
        contact = _contact(db_session)
        asset = _asset(db_session)
        db_session.commit()
        r1 = create_case(db_session, primary_contact_id=contact.contact_id, asset_id=asset.asset_id,
                          domain="AUTOMOTIVE", case_type="DIAGNOSTIC", authority=full_b5_authority,
                          idempotency_key=str(uuid.uuid4()))
        db_session.commit()

        r2 = transition_case_status(db_session, case_id=r1.object_id, new_status="CLOSED",
                                     authority=full_b5_authority, idempotency_key=str(uuid.uuid4()))
        db_session.commit()
        decision = db_session.get(CanonicalCaseDecision, r2.payload["decision_id"])
        assert decision.decision_type == "STATUS_TRANSITION"
        assert decision.new_value["case_status"] == "CLOSED"
        case = db_session.get(Case, r1.object_id)
        assert case.closed_at is not None

    def test_p04_status_transition_idempotent_replay(self, db_session, full_b5_authority):
        contact = _contact(db_session)
        asset = _asset(db_session)
        db_session.commit()
        r1 = create_case(db_session, primary_contact_id=contact.contact_id, asset_id=asset.asset_id,
                          domain="AUTOMOTIVE", case_type="DIAGNOSTIC", authority=full_b5_authority,
                          idempotency_key=str(uuid.uuid4()))
        db_session.commit()
        key = str(uuid.uuid4())
        r2 = transition_case_status(db_session, case_id=r1.object_id, new_status="IN_PROGRESS",
                                     authority=full_b5_authority, idempotency_key=key)
        db_session.commit()
        r3 = transition_case_status(db_session, case_id=r1.object_id, new_status="IN_PROGRESS",
                                     authority=full_b5_authority, idempotency_key=key)
        db_session.commit()
        assert r2.payload["decision_id"] == r3.payload["decision_id"]
        assert r3.payload.get("replay") is True

    def test_p05_participant_added(self, db_session, full_b5_authority):
        contact = _contact(db_session)
        asset = _asset(db_session)
        db_session.commit()
        r1 = create_case(db_session, primary_contact_id=contact.contact_id, asset_id=asset.asset_id,
                          domain="AUTOMOTIVE", case_type="DIAGNOSTIC", authority=full_b5_authority,
                          idempotency_key=str(uuid.uuid4()))
        db_session.commit()

        technician = _contact(db_session, "Technician")
        db_session.commit()
        r2 = add_participant(db_session, case_id=r1.object_id, contact_id=technician.contact_id,
                              participant_role="TECHNICIAN", authority=full_b5_authority,
                              idempotency_key=str(uuid.uuid4()))
        db_session.commit()
        assert r2.outcome == CaseOutcome.SUCCESS

    def test_p06_participant_removed(self, db_session, full_b5_authority):
        contact = _contact(db_session)
        asset = _asset(db_session)
        db_session.commit()
        r1 = create_case(db_session, primary_contact_id=contact.contact_id, asset_id=asset.asset_id,
                          domain="AUTOMOTIVE", case_type="DIAGNOSTIC", authority=full_b5_authority,
                          idempotency_key=str(uuid.uuid4()))
        db_session.commit()
        technician = _contact(db_session, "Tech2")
        db_session.commit()
        r2 = add_participant(db_session, case_id=r1.object_id, contact_id=technician.contact_id,
                              participant_role="TECHNICIAN", authority=full_b5_authority,
                              idempotency_key=str(uuid.uuid4()))
        db_session.commit()
        r3 = remove_participant(db_session, case_participant_id=r2.object_id, authority=full_b5_authority,
                                 idempotency_key=str(uuid.uuid4()))
        db_session.commit()
        assert r3.outcome == CaseOutcome.SUCCESS

    def test_p07_event_recorded_with_registered_type(self, db_session, full_b5_authority):
        contact = _contact(db_session)
        asset = _asset(db_session)
        db_session.commit()
        r1 = create_case(db_session, primary_contact_id=contact.contact_id, asset_id=asset.asset_id,
                          domain="AUTOMOTIVE", case_type="DIAGNOSTIC", authority=full_b5_authority,
                          idempotency_key=str(uuid.uuid4()))
        db_session.commit()

        register_event_type(db_session, event_type="DIAGNOSIS_REPORTED", semantic_class="DOMAIN_ASSERTION")
        register_event_type(db_session, event_type="CASE_OPENED", semantic_class="CPL_OPERATIONAL_FACT")
        db_session.commit()

        r2 = record_case_event(db_session, case_id=r1.object_id, event_type="DIAGNOSIS_REPORTED",
                                actor_type="RUNNER", payload={"finding": "worn brake pads"},
                                authority=full_b5_authority)
        db_session.commit()
        assert r2.outcome == CaseOutcome.SUCCESS
        assert r2.payload["semantic_class"] == "DOMAIN_ASSERTION"

    def test_p08_occurred_at_differs_from_created_at(self, db_session, full_b5_authority):
        contact = _contact(db_session)
        asset = _asset(db_session)
        db_session.commit()
        r1 = create_case(db_session, primary_contact_id=contact.contact_id, asset_id=asset.asset_id,
                          domain="AUTOMOTIVE", case_type="DIAGNOSTIC", authority=full_b5_authority,
                          idempotency_key=str(uuid.uuid4()))
        db_session.commit()
        register_event_type(db_session, event_type="DOCUMENT_RECEIVED", semantic_class="CPL_OPERATIONAL_FACT")
        db_session.commit()

        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        r2 = record_case_event(db_session, case_id=r1.object_id, event_type="DOCUMENT_RECEIVED",
                                actor_type="CONTACT", occurred_at=yesterday, authority=full_b5_authority)
        db_session.commit()
        event = db_session.get(CaseEvent, r2.object_id)
        # REQ-B5-114: occurred_at (yesterday) != created_at (today), both reconstructable
        assert event.occurred_at.date() == yesterday.date()
        assert event.created_at.date() == datetime.now(timezone.utc).date()

    def test_p09_event_correction_preserves_original(self, db_session, full_b5_authority):
        contact = _contact(db_session)
        asset = _asset(db_session)
        db_session.commit()
        r1 = create_case(db_session, primary_contact_id=contact.contact_id, asset_id=asset.asset_id,
                          domain="AUTOMOTIVE", case_type="DIAGNOSTIC", authority=full_b5_authority,
                          idempotency_key=str(uuid.uuid4()))
        db_session.commit()
        register_event_type(db_session, event_type="DIAGNOSIS_REPORTED", semantic_class="DOMAIN_ASSERTION")
        db_session.commit()
        r2 = record_case_event(db_session, case_id=r1.object_id, event_type="DIAGNOSIS_REPORTED",
                                actor_type="RUNNER", payload={"finding": "wrong finding"},
                                authority=full_b5_authority)
        db_session.commit()

        r3 = correct_case_event(db_session, event_id_to_correct=r2.object_id,
                                 corrected_payload={"finding": "correct finding"},
                                 reason="initial report was wrong", authority=full_b5_authority,
                                 idempotency_key=str(uuid.uuid4()))
        db_session.commit()
        assert r3.outcome == CaseOutcome.SUCCESS

        original = db_session.get(CaseEvent, r2.object_id)
        assert original.event_status == "SUPERSEDED"
        assert original.payload == {"finding": "wrong finding"}  # preserved, not overwritten
        corrected = db_session.get(CaseEvent, r3.object_id)
        assert corrected.payload == {"finding": "correct finding"}
        assert corrected.event_status == "CURRENT"

    def test_p10_metadata_correction_preserves_prior(self, db_session, full_b5_authority):
        contact = _contact(db_session)
        asset = _asset(db_session)
        db_session.commit()
        r1 = create_case(db_session, primary_contact_id=contact.contact_id, asset_id=asset.asset_id,
                          domain="AUTOMOTIVE", case_type="DIAGNOSTIC", title="Original title",
                          authority=full_b5_authority, idempotency_key=str(uuid.uuid4()))
        db_session.commit()

        r2 = correct_case_metadata(db_session, case_id=r1.object_id, new_title="Corrected title",
                                    reason="typo", authority=full_b5_authority,
                                    idempotency_key=str(uuid.uuid4()))
        db_session.commit()
        assert r2.outcome == CaseOutcome.SUCCESS
        case = db_session.get(Case, r1.object_id)
        assert case.title == "Corrected title"
        decision = db_session.get(CanonicalCaseDecision, r2.payload["decision_id"])
        assert decision.prior_value["title"] == "Original title"
