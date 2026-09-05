"""B4 coverage for the second implementation pass: AssetIdentifier
lifecycle, Asset creation admission, governed AssetIdentityResolution
operation family, relationship negative cases, integrated cardinality."""
import uuid

import pytest

from app.cpl.models.contact import Contact
from app.cpl.models.contact_asset_relationship import ContactAssetRelationship
from app.cpl.assets.creation import create_asset
from app.cpl.assets.identifiers import (
    add_asset_identifier, verify_asset_identifier, supersede_asset_identifier,
    invalidate_asset_identifier, dispute_asset_identifier, get_asset_identifiers,
    find_assets_by_identifier_value,
)
from app.cpl.assets.resolution import (
    request_asset_identity_resolution, record_asset_identity_resolution,
    evaluate_asset_resolution_admissibility,
)
from app.cpl.assets.relationships import establish_relationship
from app.cpl.assets.merge import admit_and_execute_asset_merge
from app.cpl.assets.outcomes import OperationOutcome
from app.cpl.identity.authority import AuthorityContext, AuthorityDeniedError
from tests.integration.test_b4_positive import _asset, _resolution, _full_dispositions
from app.db.engine import check_db_connection

pytestmark = pytest.mark.skipif(not check_db_connection(), reason="PostgreSQL not available")


class TestAssetCreationAdmission:

    def test_create_asset_success(self, db_session, full_b4_authority):
        r = create_asset(db_session, asset_domain="AUTOMOTIVE", asset_type="PASSENGER_CAR",
                          display_name="Test Car", authority=full_b4_authority, idempotency_key=str(uuid.uuid4()))
        db_session.commit()
        assert r.outcome == OperationOutcome.SUCCESS
        assert r.object_id is not None

    def test_create_asset_idempotent_replay(self, db_session, full_b4_authority):
        key = str(uuid.uuid4())
        r1 = create_asset(db_session, asset_domain="AUTOMOTIVE", asset_type="PASSENGER_CAR",
                           authority=full_b4_authority, idempotency_key=key)
        db_session.commit()
        r2 = create_asset(db_session, asset_domain="AUTOMOTIVE", asset_type="PASSENGER_CAR",
                           authority=full_b4_authority, idempotency_key=key)
        db_session.commit()
        assert r1.object_id == r2.object_id
        assert r2.payload.get("replay") is True

    def test_distinct_keys_same_payload_create_distinct_assets(self, db_session, full_b4_authority):
        # REQ-B4-013: idempotency by governed request identity, never
        # by supplied-evidence similarity.
        r1 = create_asset(db_session, asset_domain="AUTOMOTIVE", asset_type="PASSENGER_CAR",
                           authority=full_b4_authority, idempotency_key=str(uuid.uuid4()))
        db_session.commit()
        r2 = create_asset(db_session, asset_domain="AUTOMOTIVE", asset_type="PASSENGER_CAR",
                           authority=full_b4_authority, idempotency_key=str(uuid.uuid4()))
        db_session.commit()
        assert r1.object_id != r2.object_id

    def test_create_asset_denied_without_authority(self, db_session):
        weak = AuthorityContext(granted=frozenset(), actor_reference="nobody")
        with pytest.raises(AuthorityDeniedError):
            create_asset(db_session, asset_domain="AUTOMOTIVE", asset_type="PASSENGER_CAR",
                         authority=weak, idempotency_key=str(uuid.uuid4()))


class TestAssetIdentifierLifecycle:

    def test_add_and_verify(self, db_session, full_b4_authority):
        a = _asset(db_session)
        db_session.commit()
        r = add_asset_identifier(db_session, asset_id=a.asset_id, identifier_type="VIN",
                                  identifier_value="VIN-1", authority=full_b4_authority)
        db_session.commit()
        assert r.outcome == OperationOutcome.SUCCESS
        v = verify_asset_identifier(db_session, asset_identifier_id=r.object_id, authority=full_b4_authority)
        db_session.commit()
        assert v.outcome == OperationOutcome.SUCCESS

    def test_supersede_preserves_history(self, db_session, full_b4_authority):
        a = _asset(db_session)
        db_session.commit()
        r1 = add_asset_identifier(db_session, asset_id=a.asset_id, identifier_type="REGISTRATION",
                                   identifier_value="OLD-PLATE", authority=full_b4_authority)
        db_session.commit()
        r2 = supersede_asset_identifier(db_session, asset_identifier_id=r1.object_id,
                                         new_identifier_value="NEW-PLATE", new_normalized_value=None,
                                         authority=full_b4_authority)
        db_session.commit()
        assert r2.outcome == OperationOutcome.SUCCESS

        from app.cpl.models.asset_identifier import AssetIdentifier
        prior = db_session.get(AssetIdentifier, r1.object_id)
        assert prior.identifier_status == "SUPERSEDED"
        assert prior.identifier_value == "OLD-PLATE"  # REQ-B4-037: never rewritten in place

        identifiers = get_asset_identifiers(db_session, a.asset_id)
        assert len(identifiers) == 2  # both historical and current retrievable (REQ-B4-021)

    def test_asset_survives_identifier_invalidation(self, db_session, full_b4_authority):
        # REQ-B4-005: identifier invalidation MUST NOT, by itself,
        # invalidate the Asset.
        a = _asset(db_session)
        db_session.commit()
        r1 = add_asset_identifier(db_session, asset_id=a.asset_id, identifier_type="VIN",
                                   identifier_value="VIN-2", authority=full_b4_authority)
        db_session.commit()
        invalidate_asset_identifier(db_session, asset_identifier_id=r1.object_id, authority=full_b4_authority)
        db_session.commit()
        db_session.refresh(a)
        assert a.asset_status == "ACTIVE"

    def test_identifier_equality_does_not_auto_merge(self, db_session, full_b4_authority):
        # REQ-B4-022/055: identifier equality is evidence only.
        a = _asset(db_session)
        db_session.flush()
        b = _asset(db_session)
        db_session.commit()
        add_asset_identifier(db_session, asset_id=a.asset_id, identifier_type="VIN",
                              identifier_value="SHARED-VIN", authority=full_b4_authority)
        add_asset_identifier(db_session, asset_id=b.asset_id, identifier_type="VIN",
                              identifier_value="SHARED-VIN", authority=full_b4_authority)
        db_session.commit()

        candidates = find_assets_by_identifier_value(db_session, "SHARED-VIN")
        assert len(candidates) == 2  # evidence surfaced, no merge occurred
        db_session.refresh(a)
        db_session.refresh(b)
        assert a.asset_status != "MERGED"
        assert b.asset_status != "MERGED"

    def test_dispute_marks_conflict_without_deletion(self, db_session, full_b4_authority):
        a = _asset(db_session)
        db_session.commit()
        r1 = add_asset_identifier(db_session, asset_id=a.asset_id, identifier_type="VIN",
                                   identifier_value="VIN-3", authority=full_b4_authority)
        db_session.commit()
        r2 = dispute_asset_identifier(db_session, asset_identifier_id=r1.object_id, authority=full_b4_authority)
        db_session.commit()
        assert r2.outcome == OperationOutcome.SUCCESS
        from app.cpl.models.asset_identifier import AssetIdentifier
        identifier = db_session.get(AssetIdentifier, r1.object_id)
        assert identifier.identifier_status == "DISPUTED"  # not deleted


class TestAssetIdentityResolutionOperationFamily:

    def test_request_does_not_determine_identity(self, db_session, full_b4_authority):
        a = _asset(db_session)
        db_session.commit()
        r = request_asset_identity_resolution(db_session, asset_ids=[a.asset_id], resolver_type="VIR",
                                                authority=full_b4_authority)
        assert r.outcome == OperationOutcome.SUCCESS
        # No AssetIdentityResolution row was created by the request itself.
        from app.cpl.models.asset_identity_resolution import AssetIdentityResolution
        rows = db_session.query(AssetIdentityResolution).filter(AssetIdentityResolution.asset_id == a.asset_id).all()
        assert rows == []

    def test_record_and_evaluate_admissibility(self, db_session, full_b4_authority):
        a = _asset(db_session)
        db_session.commit()
        r = record_asset_identity_resolution(
            db_session, asset_id=a.asset_id, resolver_type="VIR", resolver_version="2.0",
            resolution_status="RESOLVED", canonical_identity_payload={"vin": "X"},
            authority=full_b4_authority,
        )
        db_session.commit()
        assert r.outcome == OperationOutcome.SUCCESS

        admissibility = evaluate_asset_resolution_admissibility(db_session, resolution_id=r.object_id, authority=full_b4_authority)
        assert admissibility.outcome == OperationOutcome.SUCCESS

    def test_superseded_resolution_not_admissible(self, db_session, full_b4_authority):
        a = _asset(db_session)
        db_session.commit()
        r1 = record_asset_identity_resolution(
            db_session, asset_id=a.asset_id, resolver_type="VIR", resolver_version="2.0",
            resolution_status="AMBIGUOUS", canonical_identity_payload={}, authority=full_b4_authority,
        )
        db_session.commit()
        r2 = record_asset_identity_resolution(
            db_session, asset_id=a.asset_id, resolver_type="VIR", resolver_version="2.0",
            resolution_status="RESOLVED", canonical_identity_payload={"vin": "X"},
            supersedes_resolution_id=r1.object_id, authority=full_b4_authority,
        )
        db_session.commit()
        admissibility = evaluate_asset_resolution_admissibility(db_session, resolution_id=r1.object_id, authority=full_b4_authority)
        assert admissibility.outcome == OperationOutcome.INVALID
        assert "superseded" in admissibility.detail


class TestRelationshipNegativeCoverage:

    def test_relationship_state_does_not_grant_authorization(self, db_session, full_b4_authority):
        # REQ-B4-234: structural assertion — no function in this
        # module returns or implies an authorization decision from a
        # relationship's existence. The relationship service surface
        # exposes only identity/lifecycle results (OperationResult),
        # never an authorization verdict.
        c = Contact(contact_type="PERSON", display_name="Liam")
        db_session.add(c)
        a = _asset(db_session)
        db_session.commit()
        result = establish_relationship(db_session, contact_id=c.contact_id, asset_id=a.asset_id,
                                         relationship_type="OWNER", evidence={"source": "registration"},
                                         authority=full_b4_authority, idempotency_key=str(uuid.uuid4()))
        db_session.commit()
        assert result.outcome == OperationOutcome.SUCCESS
        assert not hasattr(result, "authorized")
        assert "authoriz" not in [k.lower() for k in result.payload.keys()]

    def test_domain_resolver_cannot_directly_mutate_canonical_topology(self, db_session, full_b4_authority):
        # REQ-B4-235: the only path to Asset canonical mutation is
        # admit_and_execute_asset_merge, which always requires CPL
        # ADMIT+EXECUTE authority — a "domain resolver" acting only
        # through record_asset_identity_resolution never mutates Asset
        # rows (verified structurally: record_asset_identity_resolution
        # touches only AssetIdentityResolution, never Asset).
        a = _asset(db_session)
        db_session.commit()
        record_asset_identity_resolution(
            db_session, asset_id=a.asset_id, resolver_type="VIR", resolver_version="1.0",
            resolution_status="RESOLVED", canonical_identity_payload={}, authority=full_b4_authority,
        )
        db_session.commit()
        db_session.refresh(a)
        assert a.asset_status != "MERGED"
        assert a.merged_into_id is None

    def test_relationship_established_without_evidence_or_source_still_requires_authority(self, db_session):
        # REQ-B4-112: authenticated caller identity alone (even with
        # some authority) does not bypass the authority gate itself —
        # verified as a structural precondition.
        c = Contact(contact_type="PERSON", display_name="Mona")
        db_session.add(c)
        a = _asset(db_session)
        db_session.commit()
        weak = AuthorityContext(granted=frozenset(), actor_reference="unauthorized-caller")
        with pytest.raises(AuthorityDeniedError):
            establish_relationship(db_session, contact_id=c.contact_id, asset_id=a.asset_id,
                                    relationship_type="OWNER", evidence=None,
                                    authority=weak, idempotency_key=str(uuid.uuid4()))


class TestIntegratedCardinality:

    def test_establish_blocked_by_integrated_policy(self, db_session, full_b4_authority):
        # REQ-B4-155..161, item 5: the caller does NOT need to
        # separately call assess_relationship_compatibility — passing
        # cardinality_policy into establish_relationship itself blocks
        # the conflicting establishment.
        c1 = Contact(contact_type="PERSON", display_name="Nora")
        c2 = Contact(contact_type="PERSON", display_name="Omar")
        db_session.add_all([c1, c2])
        a = _asset(db_session)
        db_session.commit()

        policy = {"SOLE_OWNER": {"cardinality": "SOLE"}}
        r1 = establish_relationship(db_session, contact_id=c1.contact_id, asset_id=a.asset_id,
                                     relationship_type="SOLE_OWNER", evidence={"source": "title"},
                                     authority=full_b4_authority, idempotency_key=str(uuid.uuid4()),
                                     cardinality_policy=policy)
        db_session.commit()
        assert r1.outcome == OperationOutcome.SUCCESS

        r2 = establish_relationship(db_session, contact_id=c2.contact_id, asset_id=a.asset_id,
                                     relationship_type="SOLE_OWNER", evidence={"source": "title"},
                                     authority=full_b4_authority, idempotency_key=str(uuid.uuid4()),
                                     cardinality_policy=policy)
        db_session.commit()
        assert r2.outcome == OperationOutcome.CONFLICTING

        # No relationship row was created for the blocked attempt.
        rows = db_session.query(ContactAssetRelationship).filter(
            ContactAssetRelationship.asset_id == a.asset_id,
            ContactAssetRelationship.contact_id == c2.contact_id,
        ).all()
        assert rows == []

    def test_no_policy_still_default_unrestricted(self, db_session, full_b4_authority):
        # REQ-B4-158: absent policy, no universal rule is invented.
        c1 = Contact(contact_type="PERSON", display_name="Priya")
        c2 = Contact(contact_type="PERSON", display_name="Quinn")
        db_session.add_all([c1, c2])
        a = _asset(db_session)
        db_session.commit()
        r1 = establish_relationship(db_session, contact_id=c1.contact_id, asset_id=a.asset_id,
                                     relationship_type="USER", evidence={"source": "x"},
                                     authority=full_b4_authority, idempotency_key=str(uuid.uuid4()))
        db_session.commit()
        r2 = establish_relationship(db_session, contact_id=c2.contact_id, asset_id=a.asset_id,
                                     relationship_type="USER", evidence={"source": "x"},
                                     authority=full_b4_authority, idempotency_key=str(uuid.uuid4()))
        db_session.commit()
        assert r1.outcome == OperationOutcome.SUCCESS
        assert r2.outcome == OperationOutcome.SUCCESS
