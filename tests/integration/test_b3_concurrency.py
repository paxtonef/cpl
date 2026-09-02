"""B3 Concurrency Verification — C-B3-01 through C-B3-04.

These tests need TWO genuinely independent, auto-committing database
connections (unlike db_session, which wraps everything in an outer
transaction that never actually commits at the PostgreSQL level, by
design, so per-test state rolls back cleanly). Each test therefore
manages its own connections directly and cleans up explicitly.
"""
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.cpl.identity import OperationOutcome, attach_account, create_contact, get_contact
from app.cpl.identity.reconciliation import merge_contacts, propose_merge
from app.config import settings
from app.db.engine import check_db_connection

pytestmark = pytest.mark.skipif(not check_db_connection(), reason="PostgreSQL not available")


@pytest.fixture
def live_sessions():
    """Two independent, real, auto-committing sessions against the same DB."""
    engine = create_engine(str(settings.database_url), pool_pre_ping=True)
    Session = sessionmaker(bind=engine)
    s1, s2 = Session(), Session()
    created_contact_ids: list = []
    yield s1, s2, created_contact_ids
    # Explicit cleanup — these tests bypass db_session's auto-rollback,
    # so they must remove what they created.
    for cid in created_contact_ids:
        s1.execute(text("DELETE FROM cpl.identity_operations WHERE affected_object_ids @> :v"), {"v": f'["{cid}"]'})
        s1.execute(text("DELETE FROM cpl.merge_proposals WHERE source_contact_id = :c OR target_contact_id = :c"), {"c": str(cid)})
        s1.execute(text("DELETE FROM cpl.accounts WHERE contact_id = :c"), {"c": str(cid)})
        s1.execute(text("DELETE FROM cpl.contact_points WHERE contact_id = :c"), {"c": str(cid)})
    s1.commit()
    for cid in created_contact_ids:
        s1.execute(
            text("UPDATE cpl.contacts SET contact_status = 'ACTIVE', merged_into_id = NULL WHERE merged_into_id = :c"),
            {"c": str(cid)},
        )
    s1.commit()
    for cid in created_contact_ids:
        s1.execute(text("DELETE FROM cpl.contacts WHERE contact_id = :c"), {"c": str(cid)})
    s1.commit()
    s1.close()
    s2.close()
    engine.dispose()


class TestB3Concurrency:

    def test_c02_concurrent_incompatible_provider_binding(self, live_sessions, full_authority):
        """Two independent connections attempt to bind the same provider
        identity to two different Contacts. The second MUST be rejected
        rather than silently producing two valid active bindings."""
        s1, s2, created = live_sessions

        r_c1 = create_contact(s1, contact_type="PERSON", display_name="Iris A", authority=full_authority)
        s1.commit()
        created.append(r_c1.object_id)
        r_c2 = create_contact(s1, contact_type="PERSON", display_name="Iris B", authority=full_authority)
        s1.commit()
        created.append(r_c2.object_id)

        r1 = attach_account(s1, contact_id=r_c1.object_id, auth_provider="google", provider_subject_id="race-1", authority=full_authority)
        s1.commit()
        assert r1.outcome == OperationOutcome.SUCCESS

        r2 = attach_account(s2, contact_id=r_c2.object_id, auth_provider="google", provider_subject_id="race-1", authority=full_authority)
        s2.commit()
        assert r2.outcome == OperationOutcome.CONFLICTING

    def test_c04_concurrent_merge_same_source(self, live_sessions, full_authority):
        """Two independent connections attempt merges sharing the same
        source Contact. Exactly one surviving target must result —
        never a mutually incompatible double-merged state."""
        s1, s2, created = live_sessions

        r_c1 = create_contact(s1, contact_type="PERSON", display_name="Jack A", authority=full_authority)
        s1.commit()
        created.append(r_c1.object_id)
        r_c2 = create_contact(s1, contact_type="PERSON", display_name="Jack B", authority=full_authority)
        s1.commit()
        created.append(r_c2.object_id)
        r_c3 = create_contact(s1, contact_type="PERSON", display_name="Jack C", authority=full_authority)
        s1.commit()
        created.append(r_c3.object_id)

        p1 = propose_merge(s1, source_contact_id=r_c1.object_id, target_contact_id=r_c2.object_id, reason="race", authority=full_authority)
        s1.commit()
        p2 = propose_merge(s2, source_contact_id=r_c1.object_id, target_contact_id=r_c3.object_id, reason="race", authority=full_authority)
        s2.commit()

        result1 = merge_contacts(s1, proposal_id=p1.object_id, authority=full_authority)
        s1.commit()
        assert result1.outcome == OperationOutcome.SUCCESS

        result2 = merge_contacts(s2, proposal_id=p2.object_id, authority=full_authority)
        s2.commit()
        assert result2.outcome in (OperationOutcome.CONFLICTING, OperationOutcome.ALREADY_MERGED)

        final = get_contact(s1, r_c1.object_id, authority=full_authority)
        assert final.payload["contact"].merged_into_id == r_c2.object_id
