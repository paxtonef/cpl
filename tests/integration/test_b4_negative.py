"""B4 Negative Verification. Traces to REQ-B4-* per B4_REQUIREMENT_MATRIX_v0.1.md."""
import uuid

import pytest

from app.cpl.models.asset import Asset
from app.cpl.assets.merge import admit_and_execute_asset_merge, MATERIAL_DEPENDENCY_FAMILIES
from app.cpl.assets.outcomes import OperationOutcome, B4Outcome
from tests.integration.test_b4_positive import _asset, _resolution, _full_dispositions
from app.db.engine import check_db_connection

pytestmark = pytest.mark.skipif(not check_db_connection(), reason="PostgreSQL not available")


class TestB4Negative:

    def test_n01_ambiguous_resolution_blocks_merge(self, db_session, full_b4_authority):
        a = _asset(db_session)
        db_session.flush()
        b = _asset(db_session)
        res = _resolution(db_session, b.asset_id, status="AMBIGUOUS")
        db_session.commit()

        result = admit_and_execute_asset_merge(
            db_session, asset_a_id=a.asset_id, asset_b_id=b.asset_id, resolution_id=res.resolution_id,
            dependency_disposition=_full_dispositions(), authority=full_b4_authority, idempotency_key=str(uuid.uuid4()),
        )
        db_session.commit()
        assert result.outcome == B4Outcome.AMBIGUOUS
        db_session.refresh(b)
        assert b.asset_status != "MERGED"

    def test_n02_contradictory_resolution_blocks_merge(self, db_session, full_b4_authority):
        a = _asset(db_session)
        db_session.flush()
        b = _asset(db_session)
        res = _resolution(db_session, b.asset_id, status="CONTRADICTORY")
        db_session.commit()

        result = admit_and_execute_asset_merge(
            db_session, asset_a_id=a.asset_id, asset_b_id=b.asset_id, resolution_id=res.resolution_id,
            dependency_disposition=_full_dispositions(), authority=full_b4_authority, idempotency_key=str(uuid.uuid4()),
        )
        db_session.commit()
        assert result.outcome == B4Outcome.CONTRADICTORY

    def test_n03_unresolved_resolution_blocks_merge(self, db_session, full_b4_authority):
        a = _asset(db_session)
        db_session.flush()
        b = _asset(db_session)
        res = _resolution(db_session, b.asset_id, status="UNRESOLVED")
        db_session.commit()

        result = admit_and_execute_asset_merge(
            db_session, asset_a_id=a.asset_id, asset_b_id=b.asset_id, resolution_id=res.resolution_id,
            dependency_disposition=_full_dispositions(), authority=full_b4_authority, idempotency_key=str(uuid.uuid4()),
        )
        db_session.commit()
        assert result.outcome == B4Outcome.UNRESOLVED

    def test_n04_technical_failure_never_becomes_domain_outcome(self, db_session, full_b4_authority):
        # REQ-B4-032/054/170: FAILED resolution must map to FAILED, never
        # be silently reinterpreted as UNRESOLVED/AMBIGUOUS/NOT_FOUND.
        a = _asset(db_session)
        db_session.flush()
        b = _asset(db_session)
        res = _resolution(db_session, b.asset_id, status="FAILED")
        db_session.commit()

        result = admit_and_execute_asset_merge(
            db_session, asset_a_id=a.asset_id, asset_b_id=b.asset_id, resolution_id=res.resolution_id,
            dependency_disposition=_full_dispositions(), authority=full_b4_authority, idempotency_key=str(uuid.uuid4()),
        )
        db_session.commit()
        assert result.outcome == B4Outcome.FAILED
        assert result.outcome not in (B4Outcome.UNRESOLVED, B4Outcome.AMBIGUOUS, OperationOutcome.NOT_FOUND)

    def test_n05_identifier_equality_does_not_auto_merge(self, db_session, full_b4_authority):
        # No merge function exists that takes identifiers directly —
        # merge always requires a resolution_id (REQ-B4-022/047/055).
        # This test documents/asserts that structural fact: attempting
        # to reach merge via identifier-only input is not possible
        # through the exposed API surface.
        import inspect
        sig = inspect.signature(admit_and_execute_asset_merge)
        assert "resolution_id" in sig.parameters
        assert "asset_identifier" not in sig.parameters
        assert "identifier_value" not in sig.parameters

    def test_n06_missing_material_dependency_holds_merge(self, db_session, full_b4_authority):
        a = _asset(db_session)
        db_session.flush()
        b = _asset(db_session)
        res = _resolution(db_session, b.asset_id)
        db_session.commit()

        incomplete = _full_dispositions(exclude={"ExternalReference"})
        result = admit_and_execute_asset_merge(
            db_session, asset_a_id=a.asset_id, asset_b_id=b.asset_id, resolution_id=res.resolution_id,
            dependency_disposition=incomplete, authority=full_b4_authority, idempotency_key=str(uuid.uuid4()),
        )
        db_session.commit()
        assert result.outcome == B4Outcome.HOLD
        db_session.refresh(b)
        assert b.asset_status != "MERGED"

    def test_n07_blocking_dependency_disposition_rejects_merge(self, db_session, full_b4_authority):
        a = _asset(db_session)
        db_session.flush()
        b = _asset(db_session)
        res = _resolution(db_session, b.asset_id)
        db_session.commit()

        dispositions = _full_dispositions()
        dispositions["ContactAssetRelationship"] = "REJECT_CONFLICT"
        result = admit_and_execute_asset_merge(
            db_session, asset_a_id=a.asset_id, asset_b_id=b.asset_id, resolution_id=res.resolution_id,
            dependency_disposition=dispositions, authority=full_b4_authority, idempotency_key=str(uuid.uuid4()),
        )
        db_session.commit()
        assert result.outcome == OperationOutcome.CONFLICTING
        db_session.refresh(b)
        assert b.asset_status != "MERGED"

    def test_n08_survivor_override_without_reason_holds(self, db_session, full_b4_authority):
        older = _asset(db_session)
        db_session.flush()
        newer = _asset(db_session)
        res = _resolution(db_session, newer.asset_id)
        db_session.commit()

        result = admit_and_execute_asset_merge(
            db_session, asset_a_id=older.asset_id, asset_b_id=newer.asset_id, resolution_id=res.resolution_id,
            dependency_disposition=_full_dispositions(), authority=full_b4_authority, idempotency_key=str(uuid.uuid4()),
            survivor_override_asset_id=newer.asset_id, survivor_override_reason="   ",
        )
        db_session.commit()
        # REQ-B4-074: an override without a durable reason is not valid — HOLD.
        assert result.outcome == B4Outcome.HOLD

    def test_n09_self_merge_rejected(self, db_session, full_b4_authority):
        a = _asset(db_session)
        db_session.commit()
        result = admit_and_execute_asset_merge(
            db_session, asset_a_id=a.asset_id, asset_b_id=a.asset_id, resolution_id=uuid.uuid4(),
            dependency_disposition=_full_dispositions(), authority=full_b4_authority, idempotency_key=str(uuid.uuid4()),
        )
        assert result.outcome == OperationOutcome.INVALID

    def test_n10_admin_privilege_does_not_bypass_admission(self, db_session):
        # Authority without ADMIT/EXECUTE grants must be denied, no matter
        # what other privileges are present (REQ-B4-056).
        from app.cpl.identity.authority import AuthorityContext, AuthorityDeniedError
        weak_authority = AuthorityContext(granted=frozenset({"SOME_OTHER_ADMIN_PRIVILEGE"}), actor_reference="admin")
        a = _asset(db_session)
        db_session.flush()
        b = _asset(db_session)
        res = _resolution(db_session, b.asset_id)
        db_session.commit()

        with pytest.raises(AuthorityDeniedError):
            admit_and_execute_asset_merge(
                db_session, asset_a_id=a.asset_id, asset_b_id=b.asset_id, resolution_id=res.resolution_id,
                dependency_disposition=_full_dispositions(), authority=weak_authority, idempotency_key=str(uuid.uuid4()),
            )
