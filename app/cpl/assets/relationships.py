"""ContactAssetRelationship canonical decisions: ESTABLISH / END /
CORRECT / SUPERSEDE (REQ-B4-104..154, F12/F13/F14/F15/F17), plus
REQ-B4-243/244 (decision/effect consistency) and REQ-B4-252/253/254
(idempotency).

Relationship logical identity (`relationship_id`) is independent of
current canonical Contact/Asset endpoints (REQ-B4-105..108) — endpoint
canonical evolution is handled purely by navigation (see
app.cpl.assets.navigation), never by rewriting this table's rows.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.cpl.assets.authority import AssetAuthority, AuthorityContext
from app.cpl.assets.outcomes import B4Outcome, OperationOutcome, OperationResult
from app.cpl.models.contact import Contact
from app.cpl.models.asset import Asset
from app.cpl.models.contact_asset_relationship import ContactAssetRelationship
from app.cpl.models.canonical_relationship_decision import CanonicalRelationshipDecision
from app.cpl.models.relationship_mutation_request import RelationshipMutationRequest


def _idempotent_replay(session: Session, idempotency_key: str) -> Optional[OperationResult]:
    existing = session.get(RelationshipMutationRequest, idempotency_key)
    if existing is None:
        return None
    decision = session.get(CanonicalRelationshipDecision, existing.decision_id)
    return OperationResult(
        outcome=OperationOutcome.SUCCESS if decision.result == "EXECUTED" else OperationOutcome.NO_CHANGE,
        object_id=decision.relationship_id,
        payload={"decision_id": decision.decision_id, "replay": True},
    )


def establish_relationship(
    session: Session, *, contact_id: UUID, asset_id: UUID, relationship_type: str,
    evidence: Optional[dict], authority: AuthorityContext, idempotency_key: str,
    valid_from: Optional[datetime] = None, source: Optional[str] = None,
) -> OperationResult:
    """REQ-B4-104..119, REQ-B4-129. Relationship evidence != authority
    (REQ-B4-111): admission requires applicable evidence/authority
    context, not merely a self-asserted claim."""
    authority.require(AssetAuthority.MANAGE_RELATIONSHIP)

    replay = _idempotent_replay(session, idempotency_key)
    if replay is not None:
        return replay

    contact = session.get(Contact, contact_id)
    asset = session.get(Asset, asset_id)
    if contact is None or asset is None:
        return OperationResult(outcome=OperationOutcome.NOT_FOUND)

    relationship = ContactAssetRelationship(
        contact_id=contact_id, asset_id=asset_id, relationship_type=relationship_type,
        relationship_status="ACTIVE", source=source,
        valid_from=valid_from or datetime.now(timezone.utc),
    )
    session.add(relationship)
    session.flush()

    decision = _record_relationship_decision(
        session, relationship_id=relationship.relationship_id, decision_type="ESTABLISH",
        evidence=evidence, authority=authority, valid_from=relationship.valid_from,
        valid_until=None, result="EXECUTED",
    )
    _record_idempotency(session, idempotency_key, decision.decision_id)
    return OperationResult(outcome=OperationOutcome.SUCCESS, object_id=relationship.relationship_id,
                            payload={"decision_id": decision.decision_id})


def end_relationship(
    session: Session, *, relationship_id: UUID, valid_until: Optional[datetime],
    evidence: Optional[dict], authority: AuthorityContext, idempotency_key: str,
) -> OperationResult:
    """REQ-B4-130, REQ-B4-137: END is semantically distinct from CORRECT
    — it closes the valid-time interval without altering the fact that
    the relationship was previously valid."""
    authority.require(AssetAuthority.MANAGE_RELATIONSHIP)

    replay = _idempotent_replay(session, idempotency_key)
    if replay is not None:
        return replay

    relationship = session.get(ContactAssetRelationship, relationship_id)
    if relationship is None:
        return OperationResult(outcome=OperationOutcome.NOT_FOUND)
    if relationship.relationship_status == "ENDED":
        return OperationResult(outcome=OperationOutcome.NO_CHANGE, object_id=relationship_id)

    effective_until = valid_until or datetime.now(timezone.utc)
    relationship.relationship_status = "ENDED"
    relationship.valid_until = effective_until
    relationship.updated_at = datetime.now(timezone.utc)
    relationship.record_version = (relationship.record_version or 0) + 1
    session.flush()

    decision = _record_relationship_decision(
        session, relationship_id=relationship_id, decision_type="END", evidence=evidence,
        authority=authority, valid_from=relationship.valid_from, valid_until=effective_until, result="EXECUTED",
    )
    _record_idempotency(session, idempotency_key, decision.decision_id)
    return OperationResult(outcome=OperationOutcome.SUCCESS, object_id=relationship_id,
                            payload={"decision_id": decision.decision_id})


def correct_relationship_valid_time(
    session: Session, *, relationship_id: UUID, corrected_valid_from: Optional[datetime],
    corrected_valid_until: Optional[datetime], evidence: Optional[dict],
    authority: AuthorityContext, idempotency_key: str,
) -> OperationResult:
    """REQ-B4-131, REQ-B4-133..136: CORRECT retroactively revises the
    interpreted VALID TIME interval without erasing the earlier
    decision (DECISION TIME) history — the prior decision row is left
    untouched; this new CORRECT decision supersedes only its *current
    effect* (B4-CI16, B4-CI22)."""
    authority.require(AssetAuthority.MANAGE_RELATIONSHIP)

    replay = _idempotent_replay(session, idempotency_key)
    if replay is not None:
        return replay

    relationship = session.get(ContactAssetRelationship, relationship_id)
    if relationship is None:
        return OperationResult(outcome=OperationOutcome.NOT_FOUND)

    prior_decision = (
        session.query(CanonicalRelationshipDecision)
        .filter(CanonicalRelationshipDecision.relationship_id == relationship_id)
        .order_by(CanonicalRelationshipDecision.decided_at.desc())
        .first()
    )

    relationship.valid_from = corrected_valid_from if corrected_valid_from is not None else relationship.valid_from
    relationship.valid_until = corrected_valid_until if corrected_valid_until is not None else relationship.valid_until
    relationship.updated_at = datetime.now(timezone.utc)
    relationship.record_version = (relationship.record_version or 0) + 1
    session.flush()

    decision = _record_relationship_decision(
        session, relationship_id=relationship_id, decision_type="CORRECT", evidence=evidence,
        authority=authority, valid_from=relationship.valid_from, valid_until=relationship.valid_until,
        result="EXECUTED", supersedes=prior_decision.decision_id if prior_decision else None,
    )
    _record_idempotency(session, idempotency_key, decision.decision_id)
    return OperationResult(outcome=OperationOutcome.SUCCESS, object_id=relationship_id,
                            payload={"decision_id": decision.decision_id,
                                     "supersedes_decision_id": prior_decision.decision_id if prior_decision else None})


def supersede_relationship_decision(
    session: Session, *, relationship_id: UUID, evidence: Optional[dict],
    authority: AuthorityContext, idempotency_key: str,
) -> OperationResult:
    """REQ-B4-132: SUPERSEDE records that a new governed determination
    replaces a prior decision's *current effect* without asserting an
    ESTABLISH/END/CORRECT transition — e.g. re-evaluation under a
    revised policy. Distinct from CORRECT (REQ-B4-138): CORRECT revises
    valid-time interpretation of the same underlying fact; SUPERSEDE
    replaces which decision currently governs the relationship."""
    authority.require(AssetAuthority.MANAGE_RELATIONSHIP)

    replay = _idempotent_replay(session, idempotency_key)
    if replay is not None:
        return replay

    relationship = session.get(ContactAssetRelationship, relationship_id)
    if relationship is None:
        return OperationResult(outcome=OperationOutcome.NOT_FOUND)

    prior_decision = (
        session.query(CanonicalRelationshipDecision)
        .filter(CanonicalRelationshipDecision.relationship_id == relationship_id)
        .order_by(CanonicalRelationshipDecision.decided_at.desc())
        .first()
    )

    decision = _record_relationship_decision(
        session, relationship_id=relationship_id, decision_type="SUPERSEDE", evidence=evidence,
        authority=authority, valid_from=relationship.valid_from, valid_until=relationship.valid_until,
        result="EXECUTED", supersedes=prior_decision.decision_id if prior_decision else None,
    )
    _record_idempotency(session, idempotency_key, decision.decision_id)
    return OperationResult(outcome=OperationOutcome.SUCCESS, object_id=relationship_id,
                            payload={"decision_id": decision.decision_id,
                                     "supersedes_decision_id": prior_decision.decision_id if prior_decision else None})


def assess_relationship_compatibility(
    session: Session, *, asset_id: UUID, relationship_type: str, candidate_contact_id: UUID,
    policy: dict[str, dict],
) -> OperationResult:
    """REQ-B4-155..161: cardinality/compatibility is type/domain
    governed via caller-supplied `policy`, never a generic CPL rule.
    `policy[relationship_type]` may set {"cardinality": "SOLE"} to mean
    at most one ACTIVE holder of that type is compatible at a time;
    absent policy entries default to unrestricted coexistence
    (REQ-B4-158) — CPL invents no universal 'one OWNER' rule."""
    rule = policy.get(relationship_type, {})
    if rule.get("cardinality") != "SOLE":
        return OperationResult(outcome=OperationOutcome.SUCCESS, detail="coexistence permitted by policy")

    existing = (
        session.query(ContactAssetRelationship)
        .filter(
            ContactAssetRelationship.asset_id == asset_id,
            ContactAssetRelationship.relationship_type == relationship_type,
            ContactAssetRelationship.relationship_status == "ACTIVE",
            ContactAssetRelationship.contact_id != candidate_contact_id,
        )
        .all()
    )
    if not existing:
        return OperationResult(outcome=OperationOutcome.SUCCESS, detail="no existing SOLE holder")
    # REQ-B4-159/160: explicit contradiction, not silently arbitrated
    # by recency/confidence/insertion order.
    return OperationResult(
        outcome=OperationOutcome.CONFLICTING,
        detail="policy declares SOLE cardinality; existing ACTIVE holder(s) present",
        payload={"conflicting_relationship_ids": [r.relationship_id for r in existing]},
    )


def _record_relationship_decision(session: Session, *, relationship_id: UUID, decision_type: str,
                                   evidence: Optional[dict], authority: AuthorityContext,
                                   valid_from: Optional[datetime], valid_until: Optional[datetime],
                                   result: str, supersedes: Optional[UUID] = None) -> CanonicalRelationshipDecision:
    decision = CanonicalRelationshipDecision(
        relationship_id=relationship_id, decision_type=decision_type, evidence=evidence,
        authority_context=authority.as_dict(), valid_from=valid_from, valid_until=valid_until,
        result=result, supersedes_decision_id=supersedes,
    )
    session.add(decision)
    session.flush()
    return decision


def _record_idempotency(session: Session, idempotency_key: str, decision_id: UUID) -> None:
    session.add(RelationshipMutationRequest(idempotency_key=idempotency_key, decision_id=decision_id))
    session.flush()
