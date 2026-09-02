"""B3 Positive Verification — P-B3-01 through P-B3-26.

Traces to REQ-B3-* per B3_REQUIREMENT_MATRIX_v0.1.md.
"""
from datetime import datetime, timezone

import pytest

from app.cpl.identity import (
    AssertionRejected, EmailEvidence, OperationOutcome, PhoneEvidence,
    ProviderAccountEvidence, ResolutionState, VerificationAssertion,
    add_contact_point, attach_account, create_contact, detect_duplicate_contact,
    disable_account, get_contact, invalidate_contact_point, merge_contacts,
    propose_merge, resolve_authenticated_contact, resolve_contact,
    revoke_account, set_primary_contact_point, verify_contact_point,
)
from app.db.engine import check_db_connection

pytestmark = pytest.mark.skipif(not check_db_connection(), reason="PostgreSQL not available")


class TestB3Positive:

    def test_p01_get_existing_contact(self, db_session, full_authority):
        r = create_contact(db_session, contact_type="PERSON", display_name="Alice", authority=full_authority)
        db_session.commit()
        result = get_contact(db_session, r.object_id, authority=full_authority)
        assert result.outcome == OperationOutcome.SUCCESS
        assert result.object_id == r.object_id

    def test_p02_resolve_uniquely_matched_contact(self, db_session, full_authority):
        r = create_contact(db_session, contact_type="PERSON", display_name="Bob", authority=full_authority)
        add_contact_point(db_session, contact_id=r.object_id, point_type="EMAIL", raw_value="bob@example.com", authority=full_authority)
        db_session.commit()
        res = resolve_contact(db_session, [EmailEvidence("bob@example.com")], authority=full_authority)
        assert res.state == ResolutionState.MATCHED
        assert res.contact_id == r.object_id

    def test_p03_create_authorized_contact(self, db_session, full_authority):
        r = create_contact(db_session, contact_type="ORGANIZATION", display_name="Acme", authority=full_authority)
        db_session.commit()
        assert r.outcome == OperationOutcome.SUCCESS
        assert r.object_id is not None

    def test_p04_attach_contact_point(self, db_session, full_authority):
        c = create_contact(db_session, contact_type="PERSON", display_name="Carol", authority=full_authority)
        r = add_contact_point(db_session, contact_id=c.object_id, point_type="EMAIL", raw_value="carol@example.com", authority=full_authority)
        db_session.commit()
        assert r.outcome == OperationOutcome.SUCCESS

    def test_p05_accept_valid_verification_assertion(self, db_session, full_authority):
        c = create_contact(db_session, contact_type="PERSON", display_name="Dave", authority=full_authority)
        cp = add_contact_point(db_session, contact_id=c.object_id, point_type="EMAIL", raw_value="dave@example.com", authority=full_authority)
        db_session.commit()
        assertion = VerificationAssertion(
            contact_point_id=cp.object_id, verification_class="EMAIL_LINK", issuer="mail-provider",
            result="ACCEPTED", verified_at=datetime.now(timezone.utc),
        )
        r = verify_contact_point(db_session, assertion=assertion, authority=full_authority)
        db_session.commit()
        assert r.outcome == OperationOutcome.SUCCESS

    def test_p06_set_valid_primary_contact_point(self, db_session, full_authority):
        c = create_contact(db_session, contact_type="PERSON", display_name="Erin", authority=full_authority)
        cp = add_contact_point(db_session, contact_id=c.object_id, point_type="EMAIL", raw_value="erin@example.com", authority=full_authority)
        db_session.commit()
        r = set_primary_contact_point(db_session, contact_point_id=cp.object_id, authority=full_authority)
        db_session.commit()
        assert r.outcome == OperationOutcome.SUCCESS

    def test_p07_attach_external_account(self, db_session, full_authority):
        c = create_contact(db_session, contact_type="PERSON", display_name="Frank", authority=full_authority)
        db_session.commit()
        r = attach_account(db_session, contact_id=c.object_id, auth_provider="google", provider_subject_id="frank-1", authority=full_authority)
        db_session.commit()
        assert r.outcome == OperationOutcome.SUCCESS

    def test_p08_resolve_via_active_account(self, db_session, full_authority):
        c = create_contact(db_session, contact_type="PERSON", display_name="Grace", authority=full_authority)
        attach_account(db_session, contact_id=c.object_id, auth_provider="google", provider_subject_id="grace-1", authority=full_authority)
        db_session.commit()
        res = resolve_authenticated_contact(db_session, provider="google", provider_subject="grace-1", authority=full_authority)
        assert res.state == ResolutionState.MATCHED
        assert res.contact_id == c.object_id

    def test_p09_disable_account(self, db_session, full_authority):
        c = create_contact(db_session, contact_type="PERSON", display_name="Heidi", authority=full_authority)
        a = attach_account(db_session, contact_id=c.object_id, auth_provider="google", provider_subject_id="heidi-1", authority=full_authority)
        db_session.commit()
        r = disable_account(db_session, account_id=a.object_id, authority=full_authority)
        db_session.commit()
        assert r.outcome == OperationOutcome.SUCCESS

    def test_p10_revoke_account(self, db_session, full_authority):
        c = create_contact(db_session, contact_type="PERSON", display_name="Ivan", authority=full_authority)
        a = attach_account(db_session, contact_id=c.object_id, auth_provider="google", provider_subject_id="ivan-1", authority=full_authority)
        db_session.commit()
        r = revoke_account(db_session, account_id=a.object_id, authority=full_authority)
        db_session.commit()
        assert r.outcome == OperationOutcome.SUCCESS

    def test_p11_detect_plausible_duplicate(self, db_session, full_authority):
        c1 = create_contact(db_session, contact_type="PERSON", display_name="Judy A", authority=full_authority)
        c2 = create_contact(db_session, contact_type="PERSON", display_name="Judy B", authority=full_authority)
        add_contact_point(db_session, contact_id=c1.object_id, point_type="EMAIL", raw_value="judy@example.com", authority=full_authority)
        add_contact_point(db_session, contact_id=c2.object_id, point_type="EMAIL", raw_value="judy@example.com", authority=full_authority)
        db_session.commit()
        r = detect_duplicate_contact(db_session, contact_id=c1.object_id, authority=full_authority)
        assert r.outcome == OperationOutcome.SUCCESS
        assert r.payload["assessment"] in ("POSSIBLE_DUPLICATE", "STRONG_DUPLICATE_CANDIDATE")

    def test_p12_create_directional_merge_proposal(self, db_session, full_authority):
        c1 = create_contact(db_session, contact_type="PERSON", display_name="Ken A", authority=full_authority)
        c2 = create_contact(db_session, contact_type="PERSON", display_name="Ken B", authority=full_authority)
        db_session.commit()
        r = propose_merge(db_session, source_contact_id=c1.object_id, target_contact_id=c2.object_id, reason="dup", authority=full_authority)
        db_session.commit()
        assert r.outcome == OperationOutcome.SUCCESS

    def test_p13_execute_authorized_merge(self, db_session, full_authority):
        c1 = create_contact(db_session, contact_type="PERSON", display_name="Liam A", authority=full_authority)
        c2 = create_contact(db_session, contact_type="PERSON", display_name="Liam B", authority=full_authority)
        db_session.commit()
        p = propose_merge(db_session, source_contact_id=c1.object_id, target_contact_id=c2.object_id, reason="dup", authority=full_authority)
        db_session.commit()
        r = merge_contacts(db_session, proposal_id=p.object_id, authority=full_authority)
        db_session.commit()
        assert r.outcome == OperationOutcome.SUCCESS
        assert r.object_id == c2.object_id

    def test_p14_preserve_merged_source(self, db_session, full_authority):
        c1 = create_contact(db_session, contact_type="PERSON", display_name="Mia A", authority=full_authority)
        c2 = create_contact(db_session, contact_type="PERSON", display_name="Mia B", authority=full_authority)
        db_session.commit()
        p = propose_merge(db_session, source_contact_id=c1.object_id, target_contact_id=c2.object_id, reason="dup", authority=full_authority)
        db_session.commit()
        merge_contacts(db_session, proposal_id=p.object_id, authority=full_authority)
        db_session.commit()
        source = get_contact(db_session, c1.object_id, authority=full_authority)
        assert source.outcome == OperationOutcome.SUCCESS
        assert source.payload["contact"].contact_status == "MERGED"
        assert source.payload["contact"].merged_into_id == c2.object_id

    def test_p15_preserve_historical_account_context(self, db_session, full_authority):
        c1 = create_contact(db_session, contact_type="PERSON", display_name="Nina A", authority=full_authority)
        c2 = create_contact(db_session, contact_type="PERSON", display_name="Nina B", authority=full_authority)
        a = attach_account(db_session, contact_id=c1.object_id, auth_provider="google", provider_subject_id="nina-1", authority=full_authority)
        db_session.commit()
        p = propose_merge(db_session, source_contact_id=c1.object_id, target_contact_id=c2.object_id, reason="dup", authority=full_authority)
        db_session.commit()
        merge_contacts(db_session, proposal_id=p.object_id, authority=full_authority)
        db_session.commit()
        from app.cpl.models.account import Account
        acct = db_session.get(Account, a.object_id)
        assert acct.contact_id == c2.object_id  # REASSOCIATE default

    def test_p16_replay_account_binding_safely(self, db_session, full_authority):
        c = create_contact(db_session, contact_type="PERSON", display_name="Oscar", authority=full_authority)
        db_session.commit()
        r1 = attach_account(db_session, contact_id=c.object_id, auth_provider="google", provider_subject_id="oscar-1", authority=full_authority)
        db_session.commit()
        r2 = attach_account(db_session, contact_id=c.object_id, auth_provider="google", provider_subject_id="oscar-1", authority=full_authority)
        db_session.commit()
        assert r2.outcome == OperationOutcome.ALREADY_EXISTS
        assert r2.object_id == r1.object_id

    def test_p17_replay_merge_safely(self, db_session, full_authority):
        c1 = create_contact(db_session, contact_type="PERSON", display_name="Paul A", authority=full_authority)
        c2 = create_contact(db_session, contact_type="PERSON", display_name="Paul B", authority=full_authority)
        db_session.commit()
        p = propose_merge(db_session, source_contact_id=c1.object_id, target_contact_id=c2.object_id, reason="dup", authority=full_authority)
        db_session.commit()
        merge_contacts(db_session, proposal_id=p.object_id, authority=full_authority)
        db_session.commit()
        r2 = merge_contacts(db_session, proposal_id=p.object_id, authority=full_authority)
        db_session.commit()
        assert r2.outcome == OperationOutcome.ALREADY_MERGED

    def test_p18_recover_material_provenance(self, db_session, full_authority):
        c = create_contact(db_session, contact_type="PERSON", display_name="Quinn", authority=full_authority)
        db_session.commit()
        from app.cpl.models.identity_operation import IdentityOperation
        from sqlalchemy import select
        ops = db_session.execute(
            select(IdentityOperation).where(IdentityOperation.operation_type == "CREATE_CONTACT")
        ).scalars().all()
        assert any(str(c.object_id) in (op.affected_object_ids or []) for op in ops)

    def test_p19_account_reconciled_to_surviving_contact(self, db_session, full_authority):
        c1 = create_contact(db_session, contact_type="PERSON", display_name="Ruth A", authority=full_authority)
        c2 = create_contact(db_session, contact_type="PERSON", display_name="Ruth B", authority=full_authority)
        attach_account(db_session, contact_id=c1.object_id, auth_provider="apple", provider_subject_id="ruth-1", authority=full_authority)
        db_session.commit()
        p = propose_merge(db_session, source_contact_id=c1.object_id, target_contact_id=c2.object_id, reason="dup", authority=full_authority)
        db_session.commit()
        r = merge_contacts(db_session, proposal_id=p.object_id, authority=full_authority)
        db_session.commit()
        assert r.outcome == OperationOutcome.SUCCESS

    def test_p20_contactpoint_reconciled_without_manufacturing_verification(self, db_session, full_authority):
        c1 = create_contact(db_session, contact_type="PERSON", display_name="Sam A", authority=full_authority)
        c2 = create_contact(db_session, contact_type="PERSON", display_name="Sam B", authority=full_authority)
        cp = add_contact_point(db_session, contact_id=c1.object_id, point_type="EMAIL", raw_value="sam@example.com", authority=full_authority)
        db_session.commit()
        p = propose_merge(db_session, source_contact_id=c1.object_id, target_contact_id=c2.object_id, reason="dup", authority=full_authority)
        db_session.commit()
        merge_contacts(db_session, proposal_id=p.object_id, authority=full_authority)
        db_session.commit()
        from app.cpl.models.contact_point import ContactPoint
        point = db_session.get(ContactPoint, cp.object_id)
        assert point.contact_id == c2.object_id
        assert point.verification_status == "UNVERIFIED"  # not manufactured as VERIFIED

    def test_p24_valid_verification_assertion_accepted(self, db_session, full_authority):
        c = create_contact(db_session, contact_type="PERSON", display_name="Tara", authority=full_authority)
        cp = add_contact_point(db_session, contact_id=c.object_id, point_type="PHONE", raw_value="+15550001111", authority=full_authority)
        db_session.commit()
        assertion = VerificationAssertion(
            contact_point_id=cp.object_id, verification_class="SMS_OTP", issuer="sms-provider",
            result="ACCEPTED", verified_at=datetime.now(timezone.utc), replay_key="otp-abc123",
        )
        r = verify_contact_point(db_session, assertion=assertion, authority=full_authority)
        db_session.commit()
        assert r.outcome == OperationOutcome.SUCCESS

    def test_p26_same_governed_creation_request_replayed_idempotently(self, db_session, full_authority):
        r1 = create_contact(db_session, contact_type="PERSON", display_name="Uma", authority=full_authority, idempotency_key="req-xyz-1")
        db_session.commit()
        r2 = create_contact(db_session, contact_type="PERSON", display_name="Uma", authority=full_authority, idempotency_key="req-xyz-1")
        db_session.commit()
        assert r1.object_id == r2.object_id
        assert r2.payload.get("replayed") is True
