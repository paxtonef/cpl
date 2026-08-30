"""B2 Negative Verification — N01 through N24."""
import uuid
import pytest
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.base import Base
from app.db.engine import check_db_connection
from app.cpl.models.contact import Contact
from app.cpl.models.contact_point import ContactPoint
from app.cpl.models.account import Account
from app.cpl.models.asset import Asset
from app.cpl.models.asset_identifier import AssetIdentifier
from app.cpl.models.contact_asset_relationship import ContactAssetRelationship
from app.cpl.models.case import Case
from app.cpl.models.case_participant import CaseParticipant
from app.cpl.models.runner_execution import RunnerExecution
from app.cpl.models.runner_artifact import RunnerArtifact
from app.cpl.models.asset_identity_resolution import AssetIdentityResolution

pytestmark = pytest.mark.skipif(not check_db_connection(), reason="PostgreSQL not available")


def _assert_commit_fails(session, obj):
    """Add obj to session and assert that commit is rejected by the database."""
    session.add(obj)
    with pytest.raises(SQLAlchemyError):
        session.commit()
    session.rollback()


class TestB2Negative:
    """Mandatory negative verification set N01–N24."""

    def test_n01_reject_invalid_contact_type(self, db_session):
        c = Contact(contact_type="ROBOT", display_name="Bad")
        _assert_commit_fails(db_session, c)

    def test_n02_reject_invalid_contact_status(self, db_session):
        c = Contact(contact_type="PERSON", display_name="Bad", contact_status="DELETED")
        _assert_commit_fails(db_session, c)

    def test_n03_reject_contact_self_merge(self, db_session):
        c = Contact(contact_type="PERSON", display_name="Self")
        db_session.add(c)
        db_session.commit()
        # Set merged_into_id BEFORE contact_status to avoid autoflush trap:
        # After commit, the object is expired. Accessing c.contact_id to assign
        # merged_into_id triggers refresh, which autoflushes any pending dirty
        # state. If contact_status="MERGED" is already pending, autoflush sends
        # MERGED + NULL merged_into_id to PostgreSQL before merged_into_id is set.
        c.merged_into_id = c.contact_id
        c.contact_status = "MERGED"
        _assert_commit_fails(db_session, c)

    def test_n04_reject_merged_contact_without_merge_target(self, db_session):
        c = Contact(contact_type="PERSON", display_name="NoTarget")
        db_session.add(c)
        db_session.commit()
        c.contact_status = "MERGED"
        _assert_commit_fails(db_session, c)

    def test_n05_reject_orphan_contact_point(self, db_session):
        cp = ContactPoint(contact_id=uuid.uuid4(), point_type="EMAIL", raw_value="x", normalized_value="x")
        _assert_commit_fails(db_session, cp)

    def test_n06_reject_duplicate_active_primary_point_type(self, db_session):
        c = Contact(contact_type="PERSON", display_name="DupPrimary")
        db_session.add(c)
        db_session.commit()
        cp1 = ContactPoint(contact_id=c.contact_id, point_type="EMAIL", raw_value="a", normalized_value="a", is_primary=True)
        db_session.add(cp1)
        db_session.commit()
        cp2 = ContactPoint(contact_id=c.contact_id, point_type="EMAIL", raw_value="b", normalized_value="b", is_primary=True)
        _assert_commit_fails(db_session, cp2)

    def test_n07_reject_duplicate_auth_provider_identity(self, db_session):
        c = Contact(contact_type="PERSON", display_name="Auth")
        db_session.add(c)
        db_session.commit()
        a1 = Account(contact_id=c.contact_id, auth_provider="google", provider_subject_id="same", account_status="ACTIVE")
        db_session.add(a1)
        db_session.commit()
        a2 = Account(contact_id=c.contact_id, auth_provider="google", provider_subject_id="same", account_status="ACTIVE")
        _assert_commit_fails(db_session, a2)

    def test_n08_reject_invalid_asset_status(self, db_session):
        a = Asset(asset_domain="AUTOMOTIVE", asset_type="CAR", asset_status="BROKEN")
        _assert_commit_fails(db_session, a)

    def test_n09_reject_confidence_below_zero(self, db_session):
        a = Asset(asset_domain="AUTOMOTIVE", asset_type="CAR", asset_status="ACTIVE")
        db_session.add(a)
        db_session.commit()
        ai = AssetIdentifier(asset_id=a.asset_id, identifier_type="VIN", identifier_value="X", confidence=-0.1)
        _assert_commit_fails(db_session, ai)

    def test_n10_reject_confidence_above_one(self, db_session):
        a = Asset(asset_domain="AUTOMOTIVE", asset_type="CAR", asset_status="ACTIVE")
        db_session.add(a)
        db_session.commit()
        ai = AssetIdentifier(asset_id=a.asset_id, identifier_type="VIN", identifier_value="X", confidence=1.1)
        _assert_commit_fails(db_session, ai)

    def test_n11_reject_orphan_contact_asset_relationship(self, db_session):
        r = ContactAssetRelationship(contact_id=uuid.uuid4(), asset_id=uuid.uuid4(), relationship_type="OWNER", relationship_status="ACTIVE")
        _assert_commit_fails(db_session, r)

    def test_n12_reject_duplicate_current_active_relationship(self, db_session):
        c = Contact(contact_type="PERSON", display_name="Rel")
        a = Asset(asset_domain="AUTOMOTIVE", asset_type="CAR", asset_status="ACTIVE")
        db_session.add_all([c, a])
        db_session.commit()
        r1 = ContactAssetRelationship(contact_id=c.contact_id, asset_id=a.asset_id, relationship_type="OWNER", relationship_status="ACTIVE")
        db_session.add(r1)
        db_session.commit()
        r2 = ContactAssetRelationship(contact_id=c.contact_id, asset_id=a.asset_id, relationship_type="OWNER", relationship_status="ACTIVE")
        _assert_commit_fails(db_session, r2)

    def test_n13_reject_closed_case_without_closed_at(self, db_session):
        c = Contact(contact_type="PERSON", display_name="Case")
        a = Asset(asset_domain="AUTOMOTIVE", asset_type="CAR", asset_status="ACTIVE")
        db_session.add_all([c, a])
        db_session.commit()
        case = Case(primary_contact_id=c.contact_id, asset_id=a.asset_id, domain="AUTOMOTIVE", case_type="DIAGNOSTIC", case_status="CLOSED")
        _assert_commit_fails(db_session, case)

    def test_n14_reject_orphan_case_participant(self, db_session):
        p = CaseParticipant(case_id=uuid.uuid4(), contact_id=uuid.uuid4(), participant_role="REQUESTER")
        _assert_commit_fails(db_session, p)

    def test_n15_reject_duplicate_active_same_role_participant(self, db_session):
        c = Contact(contact_type="PERSON", display_name="Part")
        a = Asset(asset_domain="AUTOMOTIVE", asset_type="CAR", asset_status="ACTIVE")
        db_session.add_all([c, a])
        db_session.commit()
        case = Case(primary_contact_id=c.contact_id, asset_id=a.asset_id, domain="AUTOMOTIVE", case_type="DIAGNOSTIC")
        db_session.add(case)
        db_session.commit()
        p1 = CaseParticipant(case_id=case.case_id, contact_id=c.contact_id, participant_role="REQUESTER")
        db_session.add(p1)
        db_session.commit()
        p2 = CaseParticipant(case_id=case.case_id, contact_id=c.contact_id, participant_role="REQUESTER")
        _assert_commit_fails(db_session, p2)

    def test_n16_reject_runner_execution_self_parent(self, db_session):
        c = Contact(contact_type="PERSON", display_name="Run")
        a = Asset(asset_domain="AUTOMOTIVE", asset_type="CAR", asset_status="ACTIVE")
        db_session.add_all([c, a])
        db_session.commit()
        case = Case(primary_contact_id=c.contact_id, asset_id=a.asset_id, domain="AUTOMOTIVE", case_type="DIAGNOSTIC")
        db_session.add(case)
        db_session.commit()
        e = RunnerExecution(case_id=case.case_id, asset_id=a.asset_id, runner_type="VIR", runner_version="1.0")
        db_session.add(e)
        db_session.commit()
        e.parent_execution_id = e.execution_id
        _assert_commit_fails(db_session, e)

    def test_n17_reject_completed_execution_without_completed_at(self, db_session):
        c = Contact(contact_type="PERSON", display_name="Run")
        a = Asset(asset_domain="AUTOMOTIVE", asset_type="CAR", asset_status="ACTIVE")
        db_session.add_all([c, a])
        db_session.commit()
        case = Case(primary_contact_id=c.contact_id, asset_id=a.asset_id, domain="AUTOMOTIVE", case_type="DIAGNOSTIC")
        db_session.add(case)
        db_session.commit()
        e = RunnerExecution(case_id=case.case_id, asset_id=a.asset_id, runner_type="VIR", runner_version="1.0", execution_status="COMPLETED")
        _assert_commit_fails(db_session, e)

    def test_n18_reject_invalid_execution_chronology(self, db_session):
        from datetime import datetime, timezone, timedelta
        c = Contact(contact_type="PERSON", display_name="Run")
        a = Asset(asset_domain="AUTOMOTIVE", asset_type="CAR", asset_status="ACTIVE")
        db_session.add_all([c, a])
        db_session.commit()
        case = Case(primary_contact_id=c.contact_id, asset_id=a.asset_id, domain="AUTOMOTIVE", case_type="DIAGNOSTIC")
        db_session.add(case)
        db_session.commit()
        now = datetime.now(timezone.utc)
        e = RunnerExecution(case_id=case.case_id, asset_id=a.asset_id, runner_type="VIR", runner_version="1.0", execution_status="COMPLETED", started_at=now, completed_at=now - timedelta(hours=1))
        _assert_commit_fails(db_session, e)

    def test_n19_reject_duplicate_runner_idempotency_key(self, db_session):
        c = Contact(contact_type="PERSON", display_name="Run")
        a = Asset(asset_domain="AUTOMOTIVE", asset_type="CAR", asset_status="ACTIVE")
        db_session.add_all([c, a])
        db_session.commit()
        case = Case(primary_contact_id=c.contact_id, asset_id=a.asset_id, domain="AUTOMOTIVE", case_type="DIAGNOSTIC")
        db_session.add(case)
        db_session.commit()
        e1 = RunnerExecution(case_id=case.case_id, asset_id=a.asset_id, runner_type="VIR", runner_version="1.0", idempotency_key="key-123")
        db_session.add(e1)
        db_session.commit()
        e2 = RunnerExecution(case_id=case.case_id, asset_id=a.asset_id, runner_type="VIR", runner_version="1.0", idempotency_key="key-123")
        _assert_commit_fails(db_session, e2)

    def test_n20_reject_runner_artifact_self_supersession(self, db_session):
        c = Contact(contact_type="PERSON", display_name="Run")
        a = Asset(asset_domain="AUTOMOTIVE", asset_type="CAR", asset_status="ACTIVE")
        db_session.add_all([c, a])
        db_session.commit()
        case = Case(primary_contact_id=c.contact_id, asset_id=a.asset_id, domain="AUTOMOTIVE", case_type="DIAGNOSTIC")
        db_session.add(case)
        db_session.commit()
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        e = RunnerExecution(case_id=case.case_id, asset_id=a.asset_id, runner_type="VIR", runner_version="1.0", execution_status="COMPLETED", started_at=now, completed_at=now)
        db_session.add(e)
        db_session.commit()
        art = RunnerArtifact(execution_id=e.execution_id, artifact_type="X", schema_name="s", schema_version="1", payload={}, supersedes_artifact_id=None)
        db_session.add(art)
        db_session.commit()
        art.supersedes_artifact_id = art.artifact_id
        _assert_commit_fails(db_session, art)

    def test_n21_reject_incomplete_artifact_hash_pair(self, db_session):
        c = Contact(contact_type="PERSON", display_name="Run")
        a = Asset(asset_domain="AUTOMOTIVE", asset_type="CAR", asset_status="ACTIVE")
        db_session.add_all([c, a])
        db_session.commit()
        case = Case(primary_contact_id=c.contact_id, asset_id=a.asset_id, domain="AUTOMOTIVE", case_type="DIAGNOSTIC")
        db_session.add(case)
        db_session.commit()
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        e = RunnerExecution(case_id=case.case_id, asset_id=a.asset_id, runner_type="VIR", runner_version="1.0", execution_status="COMPLETED", started_at=now, completed_at=now)
        db_session.add(e)
        db_session.commit()
        art = RunnerArtifact(execution_id=e.execution_id, artifact_type="X", schema_name="s", schema_version="1", payload={}, hash_algorithm="sha256", content_hash=None)
        _assert_commit_fails(db_session, art)

    def test_n22_reject_asset_identity_resolution_self_supersession(self, db_session):
        a = Asset(asset_domain="AUTOMOTIVE", asset_type="CAR", asset_status="ACTIVE")
        db_session.add(a)
        db_session.commit()
        r = AssetIdentityResolution(asset_id=a.asset_id, resolver_type="VIR", resolver_version="1.0", resolution_status="RESOLVED", canonical_identity_payload={})
        db_session.add(r)
        db_session.commit()
        r.supersedes_resolution_id = r.resolution_id
        _assert_commit_fails(db_session, r)

    def test_n23_reject_invalid_resolution_status(self, db_session):
        a = Asset(asset_domain="AUTOMOTIVE", asset_type="CAR", asset_status="ACTIVE")
        db_session.add(a)
        db_session.commit()
        r = AssetIdentityResolution(asset_id=a.asset_id, resolver_type="VIR", resolver_version="1.0", resolution_status="GUESS", canonical_identity_payload={})
        _assert_commit_fails(db_session, r)

    def test_n24_confirm_forbidden_table_set_is_absent(self, db_engine):
        forbidden = [
            "vir_users", "pgdr_users", "vehicle_users",
            "pgdr_cases", "generic_faults", "generic_symptoms",
            "generic_repairs", "generic_components",
            "vehicle_health_record", "universal_diagnostic_state",
        ]
        with db_engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema IN ('cpl', 'automotive')
            """))
            existing = {row[0] for row in result}
        for name in forbidden:
            assert name not in existing, f"Forbidden table {name} must not exist"
