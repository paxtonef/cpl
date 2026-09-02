"""B3 Traceability Verification — TR-B3-01 through TR-B3-08 (representative subset)."""
import pytest
from sqlalchemy import select

from app.cpl.identity import create_contact, merge_contacts, propose_merge, verify_contact_point, VerificationAssertion, add_contact_point
from app.cpl.models.identity_operation import IdentityOperation
from app.db.engine import check_db_connection
from datetime import datetime, timezone

pytestmark = pytest.mark.skipif(not check_db_connection(), reason="PostgreSQL not available")


class TestB3Traceability:

    def test_tr01_contact_creation_provenance_recoverable(self, db_session, full_authority):
        r = create_contact(db_session, contact_type="PERSON", display_name="Kate", authority=full_authority)
        db_session.commit()
        ops = db_session.execute(
            select(IdentityOperation).where(IdentityOperation.operation_type == "CREATE_CONTACT")
        ).scalars().all()
        matching = [o for o in ops if str(r.object_id) in (o.affected_object_ids or [])]
        assert len(matching) == 1
        assert matching[0].actor_reference == "test-suite"
        assert matching[0].decision == "CREATE_CONTACT"

    def test_tr02_verification_provenance_recoverable(self, db_session, full_authority):
        c = create_contact(db_session, contact_type="PERSON", display_name="Leo", authority=full_authority)
        cp = add_contact_point(db_session, contact_id=c.object_id, point_type="EMAIL", raw_value="leo@example.com", authority=full_authority)
        db_session.commit()
        assertion = VerificationAssertion(
            contact_point_id=cp.object_id, verification_class="EMAIL_LINK", issuer="mail-provider",
            result="ACCEPTED", verified_at=datetime.now(timezone.utc),
        )
        verify_contact_point(db_session, assertion=assertion, authority=full_authority)
        db_session.commit()

        from app.cpl.models.contact_point_verification import ContactPointVerification
        rows = db_session.execute(
            select(ContactPointVerification).where(ContactPointVerification.contact_point_id == cp.object_id)
        ).scalars().all()
        assert len(rows) == 1
        assert rows[0].issuer == "mail-provider"
        assert rows[0].result == "ACCEPTED"

    def test_tr05_merge_execution_provenance_recoverable(self, db_session, full_authority):
        c1 = create_contact(db_session, contact_type="PERSON", display_name="Mona A", authority=full_authority)
        c2 = create_contact(db_session, contact_type="PERSON", display_name="Mona B", authority=full_authority)
        db_session.commit()
        p = propose_merge(db_session, source_contact_id=c1.object_id, target_contact_id=c2.object_id, reason="dup", authority=full_authority)
        db_session.commit()
        merge_contacts(db_session, proposal_id=p.object_id, authority=full_authority)
        db_session.commit()

        ops = db_session.execute(
            select(IdentityOperation).where(IdentityOperation.operation_type == "MERGE_CONTACTS")
        ).scalars().all()
        matching = [o for o in ops if str(c1.object_id) in (o.affected_object_ids or []) and str(c2.object_id) in (o.affected_object_ids or [])]
        assert len(matching) == 1
        assert matching[0].decision == "EXECUTE"
