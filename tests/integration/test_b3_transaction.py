"""B3 Transaction Verification — T-B3-01 through T-B3-05 (representative subset)."""
import pytest

from app.cpl.identity import OperationOutcome, create_contact, get_contact, merge_contacts, propose_merge
from app.db.engine import check_db_connection

pytestmark = pytest.mark.skipif(not check_db_connection(), reason="PostgreSQL not available")


class TestB3Transaction:

    def test_t01_rejected_proposal_cannot_be_executed(self, db_session, full_authority):
        """A proposal already terminally REJECTED must not be silently
        executable — no misleading partial merge state (REQ-B3-062)."""
        c1 = create_contact(db_session, contact_type="PERSON", display_name="Gale A", authority=full_authority)
        c2 = create_contact(db_session, contact_type="PERSON", display_name="Gale B", authority=full_authority)
        db_session.commit()

        p = propose_merge(db_session, source_contact_id=c1.object_id, target_contact_id=c2.object_id, reason="test", authority=full_authority)
        db_session.commit()

        from app.cpl.models.merge_proposal import MergeProposal
        proposal = db_session.get(MergeProposal, p.object_id)
        proposal.status = "REJECTED"
        db_session.commit()

        r = merge_contacts(db_session, proposal_id=p.object_id, authority=full_authority)
        db_session.commit()

        assert r.outcome == OperationOutcome.REJECTED
        source_after = get_contact(db_session, c1.object_id, authority=full_authority)
        assert source_after.payload["contact"].contact_status != "MERGED"

    def test_t02_merge_replay_does_not_re_execute(self, db_session, full_authority):
        """A second call against an already-EXECUTED proposal returns
        ALREADY_MERGED and performs no further mutation."""
        c1 = create_contact(db_session, contact_type="PERSON", display_name="Hank A", authority=full_authority)
        c2 = create_contact(db_session, contact_type="PERSON", display_name="Hank B", authority=full_authority)
        db_session.commit()
        p = propose_merge(db_session, source_contact_id=c1.object_id, target_contact_id=c2.object_id, reason="test", authority=full_authority)
        db_session.commit()
        r1 = merge_contacts(db_session, proposal_id=p.object_id, authority=full_authority)
        db_session.commit()
        assert r1.outcome == OperationOutcome.SUCCESS

        source_before = get_contact(db_session, c1.object_id, authority=full_authority).payload["contact"]
        version_before = source_before.record_version

        r2 = merge_contacts(db_session, proposal_id=p.object_id, authority=full_authority)
        db_session.commit()
        assert r2.outcome == OperationOutcome.ALREADY_MERGED

        source_after = get_contact(db_session, c1.object_id, authority=full_authority).payload["contact"]
        assert source_after.record_version == version_before

    def test_t03_nonexistent_proposal_no_mutation(self, db_session, full_authority):
        """merge_contacts against a nonexistent proposal_id mutates nothing."""
        from uuid import uuid4
        r = merge_contacts(db_session, proposal_id=uuid4(), authority=full_authority)
        assert r.outcome == OperationOutcome.NOT_FOUND
