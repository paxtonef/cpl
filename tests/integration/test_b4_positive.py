"""B4 Positive Verification. Traces to REQ-B4-* per B4_REQUIREMENT_MATRIX_v0.1.md."""
import uuid
from datetime import datetime, timezone, timedelta

import pytest

from app.cpl.models.asset import Asset
from app.cpl.models.asset_identity_resolution import AssetIdentityResolution
from app.cpl.models.canonical_asset_identity_decision import CanonicalAssetIdentityDecision
from app.cpl.models.contact import Contact
from app.cpl.models.contact_asset_relationship import ContactAssetRelationship
from app.cpl.models.external_reference import ExternalReference
from app.cpl.assets.merge import admit_and_execute_asset_merge, correct_asset_identity, MATERIAL_DEPENDENCY_FAMILIES
from app.cpl.assets.relationships import establish_relationship, end_relationship, correct_relationship_valid_time
from app.cpl.assets.navigation import current_asset_id, current_contact_id, relationship_current_view, external_reference_current_view
from app.cpl.assets.outcomes import OperationOutcome, B4Outcome
from app.db.engine import check_db_connection

pytestmark = pytest.mark.skipif(not check_db_connection(), reason="PostgreSQL not available")


def _full_dispositions(exclude=None):
    exclude = exclude or set()
    return {f: "PRESERVE" for f in MATERIAL_DEPENDENCY_FAMILIES if f not in exclude}


def _asset(session, **kw):
    a = Asset(asset_domain="AUTOMOTIVE", asset_type="PASSENGER_CAR", asset_status="ACTIVE", **kw)
    session.add(a)
    session.flush()
    return a


def _resolution(session, asset_id, status="RESOLVED"):
    r = AssetIdentityResolution(
        asset_id=asset_id, resolver_type="VIR", resolver_version="1.0",
        resolution_status=status, canonical_identity_payload={"note": "test"},
    )
    session.add(r)
    session.flush()
    return r


class TestB4Positive:

    def test_p01_asset_creation(self, db_session):
        a = _asset(db_session, display_name="Peugeot 3008")
        db_session.commit()
        assert a.asset_id is not None
        assert a.asset_status == "ACTIVE"

    def test_p02_merge_established_survivor_wins(self, db_session, full_b4_authority):
        # REQ-B4-070..072: established (earlier) Asset survives over later duplicate.
        older = _asset(db_session)
        db_session.flush()
        newer = _asset(db_session)
        res = _resolution(db_session, newer.asset_id)
        db_session.commit()

        result = admit_and_execute_asset_merge(
            db_session, asset_a_id=older.asset_id, asset_b_id=newer.asset_id,
            resolution_id=res.resolution_id, dependency_disposition=_full_dispositions(),
            authority=full_b4_authority, idempotency_key=str(uuid.uuid4()),
        )
        db_session.commit()
        assert result.outcome == OperationOutcome.SUCCESS
        assert result.object_id == older.asset_id  # established survives
        db_session.refresh(newer)
        assert newer.asset_status == "MERGED"
        assert newer.merged_into_id == older.asset_id

    def test_p03_merge_records_decision(self, db_session, full_b4_authority):
        a = _asset(db_session)
        db_session.flush()
        b = _asset(db_session)
        res = _resolution(db_session, b.asset_id)
        db_session.commit()

        result = admit_and_execute_asset_merge(
            db_session, asset_a_id=a.asset_id, asset_b_id=b.asset_id,
            resolution_id=res.resolution_id, dependency_disposition=_full_dispositions(),
            authority=full_b4_authority, idempotency_key=str(uuid.uuid4()),
        )
        db_session.commit()
        decision = db_session.get(CanonicalAssetIdentityDecision, result.payload["decision_id"])
        assert decision.decision_type == "MERGE"
        assert decision.result == "EXECUTED"
        assert decision.resolution_id == res.resolution_id

    def test_p04_merge_idempotent_replay(self, db_session, full_b4_authority):
        a = _asset(db_session)
        db_session.flush()
        b = _asset(db_session)
        res = _resolution(db_session, b.asset_id)
        db_session.commit()
        key = str(uuid.uuid4())

        r1 = admit_and_execute_asset_merge(
            db_session, asset_a_id=a.asset_id, asset_b_id=b.asset_id, resolution_id=res.resolution_id,
            dependency_disposition=_full_dispositions(), authority=full_b4_authority, idempotency_key=key,
        )
        db_session.commit()
        r2 = admit_and_execute_asset_merge(
            db_session, asset_a_id=a.asset_id, asset_b_id=b.asset_id, resolution_id=res.resolution_id,
            dependency_disposition=_full_dispositions(), authority=full_b4_authority, idempotency_key=key,
        )
        db_session.commit()
        assert r1.payload["decision_id"] == r2.payload["decision_id"]
        assert r2.payload.get("replay") is True

    def test_p05_correction_restores_independent_assets(self, db_session, full_b4_authority):
        a = _asset(db_session)
        db_session.flush()
        b = _asset(db_session)
        res1 = _resolution(db_session, b.asset_id)
        db_session.commit()

        merge_result = admit_and_execute_asset_merge(
            db_session, asset_a_id=a.asset_id, asset_b_id=b.asset_id, resolution_id=res1.resolution_id,
            dependency_disposition=_full_dispositions(), authority=full_b4_authority, idempotency_key=str(uuid.uuid4()),
        )
        db_session.commit()

        res2 = _resolution(db_session, b.asset_id, status="NOT_SAME_PHYSICAL_ASSET" if False else "RESOLVED")
        db_session.commit()

        corr = correct_asset_identity(
            db_session, decision_id_to_correct=merge_result.payload["decision_id"],
            new_resolution_id=res2.resolution_id, authority=full_b4_authority,
            idempotency_key=str(uuid.uuid4()), reason="later evidence contradicted merge",
        )
        db_session.commit()
        assert corr.outcome == OperationOutcome.SUCCESS
        db_session.refresh(b)
        assert b.asset_status == "ACTIVE"
        assert b.merged_into_id is None
        # REQ-B4-065/066: original merge decision preserved untouched.
        original = db_session.get(CanonicalAssetIdentityDecision, merge_result.payload["decision_id"])
        assert original.result == "EXECUTED"
        assert original.decision_type == "MERGE"

    def test_p06_survivor_override_with_reason(self, db_session, full_b4_authority):
        older = _asset(db_session)
        db_session.flush()
        newer = _asset(db_session)
        res = _resolution(db_session, newer.asset_id)
        db_session.commit()

        result = admit_and_execute_asset_merge(
            db_session, asset_a_id=older.asset_id, asset_b_id=newer.asset_id, resolution_id=res.resolution_id,
            dependency_disposition=_full_dispositions(), authority=full_b4_authority, idempotency_key=str(uuid.uuid4()),
            survivor_override_asset_id=newer.asset_id, survivor_override_reason="newer carries authoritative current projection",
        )
        db_session.commit()
        assert result.outcome == OperationOutcome.SUCCESS
        assert result.object_id == newer.asset_id
        decision = db_session.get(CanonicalAssetIdentityDecision, result.payload["decision_id"])
        assert decision.survivor_rule_applied == "RULE_3_GOVERNED_OVERRIDE"
        assert decision.survivor_override_reason

    def test_p07_relationship_establish(self, db_session, full_b4_authority):
        c = Contact(contact_type="PERSON", display_name="Dana")
        db_session.add(c)
        a = _asset(db_session)
        db_session.commit()

        result = establish_relationship(
            db_session, contact_id=c.contact_id, asset_id=a.asset_id, relationship_type="OWNER",
            evidence={"source": "registration"}, authority=full_b4_authority, idempotency_key=str(uuid.uuid4()),
        )
        db_session.commit()
        assert result.outcome == OperationOutcome.SUCCESS
        rel = db_session.get(ContactAssetRelationship, result.object_id)
        assert rel.relationship_status == "ACTIVE"

    def test_p08_relationship_end_then_correct_preserves_history(self, db_session, full_b4_authority):
        c = Contact(contact_type="PERSON", display_name="Eve")
        db_session.add(c)
        a = _asset(db_session)
        db_session.commit()

        est = establish_relationship(
            db_session, contact_id=c.contact_id, asset_id=a.asset_id, relationship_type="OWNER",
            evidence=None, authority=full_b4_authority, idempotency_key=str(uuid.uuid4()),
        )
        db_session.commit()

        ended = end_relationship(
            db_session, relationship_id=est.object_id, valid_until=None, evidence=None,
            authority=full_b4_authority, idempotency_key=str(uuid.uuid4()),
        )
        db_session.commit()
        assert ended.outcome == OperationOutcome.SUCCESS

        # REQ-B4-133..136: retroactive valid-time correction preserves decision history.
        corrected = correct_relationship_valid_time(
            db_session, relationship_id=est.object_id,
            corrected_valid_from=datetime.now(timezone.utc) - timedelta(days=10),
            corrected_valid_until=None, evidence={"reason": "later evidence"},
            authority=full_b4_authority, idempotency_key=str(uuid.uuid4()),
        )
        db_session.commit()
        assert corrected.outcome == OperationOutcome.SUCCESS
        assert corrected.payload["supersedes_decision_id"] == ended.payload["decision_id"]

    def test_p09_historical_vs_current_navigation_after_merge(self, db_session, full_b4_authority):
        c = Contact(contact_type="PERSON", display_name="Frank")
        db_session.add(c)
        older = _asset(db_session)
        db_session.flush()
        newer = _asset(db_session)
        db_session.commit()

        est = establish_relationship(
            db_session, contact_id=c.contact_id, asset_id=newer.asset_id, relationship_type="OWNER",
            evidence=None, authority=full_b4_authority, idempotency_key=str(uuid.uuid4()),
        )
        db_session.commit()

        res = _resolution(db_session, newer.asset_id)
        db_session.commit()
        admit_and_execute_asset_merge(
            db_session, asset_a_id=older.asset_id, asset_b_id=newer.asset_id, resolution_id=res.resolution_id,
            dependency_disposition=_full_dispositions(), authority=full_b4_authority, idempotency_key=str(uuid.uuid4()),
        )
        db_session.commit()

        rel = db_session.get(ContactAssetRelationship, est.object_id)
        view = relationship_current_view(db_session, rel)
        # REQ-B4-255/257/258: historical endpoint preserved, current navigation follows successor.
        assert view["historical_asset_id"] == newer.asset_id
        assert view["current_asset_id"] == older.asset_id

    def test_p10_external_reference_current_navigation_after_merge(self, db_session, full_b4_authority):
        older = _asset(db_session)
        db_session.flush()
        newer = _asset(db_session)
        db_session.commit()

        ext = ExternalReference(entity_type="asset", entity_id=newer.asset_id,
                                 reference_system="VIR", reference_type="VIN", reference_value="VIN-XYZ")
        db_session.add(ext)
        db_session.commit()

        res = _resolution(db_session, newer.asset_id)
        db_session.commit()
        admit_and_execute_asset_merge(
            db_session, asset_a_id=older.asset_id, asset_b_id=newer.asset_id, resolution_id=res.resolution_id,
            dependency_disposition=_full_dispositions(), authority=full_b4_authority, idempotency_key=str(uuid.uuid4()),
        )
        db_session.commit()

        view = external_reference_current_view(db_session, ext)
        # REQ-B4-259: historical target preserved, current navigation follows successor.
        assert view["historical_target"] == newer.asset_id
        assert view["current_target"] == older.asset_id
