"""B4 additional coverage: DomainProjection, ExternalReference lifecycle,
relationship SUPERSEDE/cardinality, and decision/effect atomicity under
injected failure (REQ-B4-241..245)."""
import uuid
from unittest.mock import patch

import pytest
from sqlalchemy.exc import IntegrityError

from app.cpl.models.asset import Asset
from app.cpl.models.contact import Contact
from app.cpl.models.canonical_asset_identity_decision import CanonicalAssetIdentityDecision
from app.cpl.assets.merge import admit_and_execute_asset_merge
from app.cpl.assets.relationships import establish_relationship, supersede_relationship_decision, assess_relationship_compatibility
from app.cpl.assets.projections import attach_domain_projection, supersede_domain_projection, assess_projection_conflict
from app.cpl.assets.external_references import add_external_reference, supersede_external_reference, invalidate_external_reference
from app.cpl.assets.outcomes import OperationOutcome
from tests.integration.test_b4_positive import _asset, _resolution, _full_dispositions
from app.db.engine import check_db_connection

pytestmark = pytest.mark.skipif(not check_db_connection(), reason="PostgreSQL not available")


class TestB4DomainProjection:

    def test_attach_and_supersede_preserves_history(self, db_session, full_b4_authority):
        a = _asset(db_session)
        db_session.commit()

        r1 = attach_domain_projection(
            db_session, asset_id=a.asset_id, projection_type="VEHICLE_DETAIL",
            payload={"make": "Peugeot"}, domain_authority="VIR", source_resolution_id=None,
            authority=full_b4_authority,
        )
        db_session.commit()
        assert r1.outcome == OperationOutcome.SUCCESS

        r2 = supersede_domain_projection(
            db_session, projection_id=r1.object_id, new_payload={"make": "Peugeot", "model": "3008"},
            domain_authority="VIR", source_resolution_id=None, authority=full_b4_authority,
        )
        db_session.commit()
        assert r2.outcome == OperationOutcome.SUCCESS
        assert r2.payload["supersedes_projection_id"] == r1.object_id

        from app.cpl.models.domain_projection import DomainProjection
        prior = db_session.get(DomainProjection, r1.object_id)
        assert prior.projection_status == "SUPERSEDED"  # REQ-B4-100: history preserved, not deleted

    def test_conflicting_current_projections_reported_not_arbitrated(self, db_session, full_b4_authority):
        a = _asset(db_session)
        db_session.commit()
        attach_domain_projection(db_session, asset_id=a.asset_id, projection_type="VEHICLE_DETAIL",
                                  payload={"make": "A"}, domain_authority="VIR", source_resolution_id=None,
                                  authority=full_b4_authority)
        attach_domain_projection(db_session, asset_id=a.asset_id, projection_type="VEHICLE_DETAIL",
                                  payload={"make": "B"}, domain_authority="PGDR", source_resolution_id=None,
                                  authority=full_b4_authority)
        db_session.commit()
        result = assess_projection_conflict(db_session, a.asset_id, "VEHICLE_DETAIL")
        # REQ-B4-101: generic CPL does not arbitrarily pick one.
        assert result.outcome == OperationOutcome.CONFLICTING


class TestB4ExternalReference:

    def test_supersede_preserves_historical_row(self, db_session, full_b4_authority):
        a = _asset(db_session)
        db_session.commit()
        r1 = add_external_reference(db_session, entity_type="asset", entity_id=a.asset_id,
                                      reference_system="VIR", reference_type="VIN", reference_value="VIN-OLD",
                                      authority=full_b4_authority)
        db_session.commit()
        r2 = supersede_external_reference(db_session, external_reference_id=r1.object_id,
                                           new_reference_value="VIN-NEW", authority=full_b4_authority)
        db_session.commit()
        assert r2.outcome == OperationOutcome.SUCCESS

        from app.cpl.models.external_reference import ExternalReference
        prior = db_session.get(ExternalReference, r1.object_id)
        assert prior.reference_status == "SUPERSEDED"
        assert prior.reference_value == "VIN-OLD"  # never rewritten in place

    def test_invalidate(self, db_session, full_b4_authority):
        a = _asset(db_session)
        db_session.commit()
        r1 = add_external_reference(db_session, entity_type="asset", entity_id=a.asset_id,
                                      reference_system="VIR", reference_type="VIN", reference_value="VIN-Z",
                                      authority=full_b4_authority)
        db_session.commit()
        r2 = invalidate_external_reference(db_session, external_reference_id=r1.object_id, authority=full_b4_authority)
        db_session.commit()
        assert r2.outcome == OperationOutcome.SUCCESS


class TestB4RelationshipSupersedeAndCardinality:

    def test_supersede_decision_chains_to_prior(self, db_session, full_b4_authority):
        c = Contact(contact_type="PERSON", display_name="Gina")
        db_session.add(c)
        a = _asset(db_session)
        db_session.commit()
        est = establish_relationship(db_session, contact_id=c.contact_id, asset_id=a.asset_id,
                                      relationship_type="OWNER", evidence=None,
                                      authority=full_b4_authority, idempotency_key=str(uuid.uuid4()))
        db_session.commit()
        sup = supersede_relationship_decision(db_session, relationship_id=est.object_id, evidence={"reason": "policy update"},
                                               authority=full_b4_authority, idempotency_key=str(uuid.uuid4()))
        db_session.commit()
        assert sup.outcome == OperationOutcome.SUCCESS
        assert sup.payload["supersedes_decision_id"] == est.payload["decision_id"]

    def test_sole_cardinality_policy_conflict(self, db_session, full_b4_authority):
        c1 = Contact(contact_type="PERSON", display_name="Holly")
        c2 = Contact(contact_type="PERSON", display_name="Ivan")
        db_session.add_all([c1, c2])
        a = _asset(db_session)
        db_session.commit()
        establish_relationship(db_session, contact_id=c1.contact_id, asset_id=a.asset_id,
                                relationship_type="SOLE_OWNER", evidence=None,
                                authority=full_b4_authority, idempotency_key=str(uuid.uuid4()))
        db_session.commit()

        policy = {"SOLE_OWNER": {"cardinality": "SOLE"}}
        result = assess_relationship_compatibility(db_session, asset_id=a.asset_id, relationship_type="SOLE_OWNER",
                                                     candidate_contact_id=c2.contact_id, policy=policy)
        assert result.outcome == OperationOutcome.CONFLICTING

    def test_no_policy_allows_coexistence(self, db_session, full_b4_authority):
        # REQ-B4-158: no universal cardinality invented absent policy.
        c1 = Contact(contact_type="PERSON", display_name="Jack")
        c2 = Contact(contact_type="PERSON", display_name="Kate")
        db_session.add_all([c1, c2])
        a = _asset(db_session)
        db_session.commit()
        establish_relationship(db_session, contact_id=c1.contact_id, asset_id=a.asset_id,
                                relationship_type="USER", evidence=None,
                                authority=full_b4_authority, idempotency_key=str(uuid.uuid4()))
        db_session.commit()
        result = assess_relationship_compatibility(db_session, asset_id=a.asset_id, relationship_type="USER",
                                                     candidate_contact_id=c2.contact_id, policy={})
        assert result.outcome == OperationOutcome.SUCCESS


class TestB4FailureConsistency:

    def test_injected_failure_after_decision_leaves_no_partial_transition(self, db_session, full_b4_authority):
        """REQ-B4-241/242/245: if the canonical Asset mutation fails
        after the CanonicalAssetIdentityDecision is written, the whole
        governed transition must roll back — no partial success may
        become visible."""
        a = _asset(db_session)
        db_session.flush()
        b = _asset(db_session)
        res = _resolution(db_session, b.asset_id)
        db_session.commit()

        # Force the *second* session.flush() inside admit_and_execute_asset_merge
        # (the one that persists the canonical Asset mutation, after the
        # decision row has already been flushed) to raise.
        from sqlalchemy.orm import Session as OrmSession
        original_flush = OrmSession.flush
        call_count = {"n": 0}

        def failing_flush(self, *args, **kwargs):
            call_count["n"] += 1
            # calls: 1=idempotency lookup n/a, decision record flush is
            # call #1 inside _record_decision; the loser mutation flush
            # is call #2. Fail on the mutation flush only.
            if call_count["n"] == 2:
                raise IntegrityError("simulated failure", None, None)
            return original_flush(self, *args, **kwargs)

        key = str(uuid.uuid4())
        with pytest.raises(IntegrityError):
            with db_session.begin_nested():
                with patch.object(OrmSession, "flush", failing_flush):
                    admit_and_execute_asset_merge(
                        db_session, asset_a_id=a.asset_id, asset_b_id=b.asset_id, resolution_id=res.resolution_id,
                        dependency_disposition=_full_dispositions(), authority=full_b4_authority, idempotency_key=key,
                    )
        # begin_nested()'s context manager issued ROLLBACK TO SAVEPOINT on
        # the exception above — the earlier commits of a/b/res (outside
        # the savepoint) remain intact; only the failed merge attempt
        # inside the savepoint was discarded.

        # Nothing from the failed attempt is visible: no decision, no
        # mutated asset status, no idempotency row.
        decisions = db_session.query(CanonicalAssetIdentityDecision).filter(
            CanonicalAssetIdentityDecision.source_asset_id.in_([a.asset_id, b.asset_id])
        ).all()
        assert decisions == []
        db_session.refresh(b)
        assert b.asset_status != "MERGED"
        assert b.merged_into_id is None
