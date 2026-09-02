"""Primitives 12-14: detect_duplicate_contact, propose_merge, merge_contacts.

Implements the frozen related-object reconciliation matrix
(B3_REQUIREMENT_MATRIX_v0.1.md Section 7):

    Accounts                    -> REASSOCIATE (default)
    ContactPoints                -> REASSOCIATE where admissible
    ContactAssetRelationships    -> PRESERVE (default; no code needed,
                                     they remain correctly attached to
                                     the historical source Contact)
    CaseParticipants             -> PRESERVE (default; same as above)
    ExternalReferences           -> PRESERVE (default; same as above)

The reconciliation ladder ASSESS -> PROPOSE -> AUTHORIZE -> EXECUTE
(FC-07 of the WHAT Freeze Challenge) is enforced as:
    detect_duplicate_contact  -> ASSESS  (wide authority, no mutation)
    propose_merge              -> PROPOSE (durable MergeProposal, no mutation)
    merge_contacts              -> AUTHORIZE + EXECUTE, gated on both an
                                    admissible PROPOSED MergeProposal AND
                                    the caller holding AUTHORIZE_MERGE +
                                    EXECUTE_MERGE authority.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.cpl.identity.authority import Authority, AuthorityContext
from app.cpl.identity.outcomes import OperationOutcome, OperationResult
from app.cpl.identity.provenance import record_operation
from app.cpl.models.account import Account
from app.cpl.models.contact import Contact
from app.cpl.models.contact_point import ContactPoint
from app.cpl.models.merge_proposal import MergeProposal


class DuplicateAssessment:
    NO_DUPLICATE_INDICATION = "NO_DUPLICATE_INDICATION"
    POSSIBLE_DUPLICATE = "POSSIBLE_DUPLICATE"
    STRONG_DUPLICATE_CANDIDATE = "STRONG_DUPLICATE_CANDIDATE"
    UNRESOLVED = "UNRESOLVED"


def detect_duplicate_contact(session: Session, *, contact_id: UUID, authority: AuthorityContext) -> OperationResult:
    """Primitive 12 (REQ-B3-039..041). Pure assessment — no mutation,
    no merge authority conferred by any result (REQ-B3-041)."""
    authority.require(Authority.ASSESS_DUPLICATE)

    contact = session.get(Contact, contact_id)
    if contact is None:
        return OperationResult(outcome=OperationOutcome.NOT_FOUND)

    points = session.execute(
        select(ContactPoint).where(
            ContactPoint.contact_id == contact_id,
            ContactPoint.valid_until.is_(None),
        )
    ).scalars().all()

    candidates: dict[UUID, str] = {}
    for p in points:
        others = session.execute(
            select(ContactPoint).where(
                ContactPoint.point_type == p.point_type,
                ContactPoint.normalized_value == p.normalized_value,
                ContactPoint.valid_until.is_(None),
                ContactPoint.contact_id != contact_id,
            )
        ).scalars().all()
        for o in others:
            other_contact = session.get(Contact, o.contact_id)
            if other_contact is None or other_contact.contact_status == "MERGED":
                continue
            strength = "STRONG" if (p.verification_status == "VERIFIED" and o.verification_status == "VERIFIED") else "WEAK"
            if candidates.get(o.contact_id) != "STRONG":
                candidates[o.contact_id] = strength

    if not candidates:
        assessment = DuplicateAssessment.NO_DUPLICATE_INDICATION
    elif "STRONG" in candidates.values():
        assessment = DuplicateAssessment.STRONG_DUPLICATE_CANDIDATE
    else:
        assessment = DuplicateAssessment.POSSIBLE_DUPLICATE

    return OperationResult(
        outcome=OperationOutcome.SUCCESS,
        object_id=contact_id,
        payload={"assessment": assessment, "candidate_contact_ids": list(candidates.keys())},
    )


def propose_merge(
    session: Session,
    *,
    source_contact_id: UUID,
    target_contact_id: UUID,
    reason: Optional[str],
    authority: AuthorityContext,
) -> OperationResult:
    """Primitive 13 (REQ-B3-042..044). Creates a durable proposal.
    MUST NOT mutate either Contact (REQ-B3-042)."""
    authority.require(Authority.PROPOSE_MERGE)

    if source_contact_id == target_contact_id:
        return OperationResult(outcome=OperationOutcome.INVALID, detail="source and target must differ")

    source = session.get(Contact, source_contact_id)
    target = session.get(Contact, target_contact_id)
    if source is None or target is None:
        return OperationResult(outcome=OperationOutcome.NOT_FOUND)

    proposal = MergeProposal(
        source_contact_id=source_contact_id,
        target_contact_id=target_contact_id,
        reason=reason,
        proposed_by=authority.actor_reference,
        status="PROPOSED",
    )
    session.add(proposal)
    session.flush()

    record_operation(
        session,
        operation_type="PROPOSE_MERGE",
        decision="PROPOSE",
        result=OperationOutcome.SUCCESS.value,
        actor_reference=authority.actor_reference,
        authority_context=authority.as_dict(),
        evidence_reference={"reason": reason} if reason else None,
        affected_object_ids=[str(proposal.proposal_id), str(source_contact_id), str(target_contact_id)],
    )
    return OperationResult(outcome=OperationOutcome.SUCCESS, object_id=proposal.proposal_id)


def _reconcile_accounts(session: Session, source_id: UUID, target_id: UUID) -> Optional[str]:
    """Accounts: REASSOCIATE default (Requirement Matrix v0.1 REQ-B3-101..104).
    Returns a rejection reason string on conflict, or None on success."""
    accounts = session.execute(select(Account).where(Account.contact_id == source_id)).scalars().all()
    for acct in accounts:
        conflict = session.execute(
            select(Account).where(
                Account.contact_id == target_id,
                Account.auth_provider == acct.auth_provider,
                Account.provider_subject_id == acct.provider_subject_id,
            )
        ).scalar_one_or_none()
        if conflict is not None:
            # REQ-B3-103: equivalent binding already on target => PRESERVE
            # history on source, no duplicate current binding needed.
            continue
        acct.contact_id = target_id
        try:
            session.flush()
        except IntegrityError:
            session.rollback()
            return "incompatible Account binding on reassociation"
    return None


def _reconcile_contact_points(session: Session, source_id: UUID, target_id: UUID) -> Optional[str]:
    """ContactPoints: REASSOCIATE where admissible (REQ-B3-105..109).
    Verification state is preserved, not re-manufactured (REQ-B3-106).
    Primary conflicts are never silently propagated (REQ-B3-108)."""
    points = session.execute(
        select(ContactPoint).where(ContactPoint.contact_id == source_id, ContactPoint.valid_until.is_(None))
    ).scalars().all()

    for pt in points:
        equivalent = session.execute(
            select(ContactPoint).where(
                ContactPoint.contact_id == target_id,
                ContactPoint.point_type == pt.point_type,
                ContactPoint.normalized_value == pt.normalized_value,
                ContactPoint.valid_until.is_(None),
            )
        ).scalar_one_or_none()
        if equivalent is not None:
            # REQ-B3-107: equivalent point already active on target =>
            # preserve source history, do not duplicate current relationship.
            continue

        target_primary = None
        if pt.is_primary:
            target_primary = session.execute(
                select(ContactPoint).where(
                    ContactPoint.contact_id == target_id,
                    ContactPoint.point_type == pt.point_type,
                    ContactPoint.is_primary.is_(True),
                    ContactPoint.valid_until.is_(None),
                )
            ).scalar_one_or_none()

        pt.contact_id = target_id
        if target_primary is not None:
            # REQ-B3-108: target's existing primary wins; reassociated
            # point becomes non-primary rather than causing a conflict.
            pt.is_primary = False
        pt.updated_at = datetime.now(timezone.utc)
        try:
            session.flush()
        except IntegrityError:
            session.rollback()
            return "ContactPoint primary conflict on reassociation"
    return None


def merge_contacts(
    session: Session,
    *,
    proposal_id: UUID,
    authority: AuthorityContext,
) -> OperationResult:
    """Primitive 14 (REQ-B3-045..066). Highest-authority B3 mutation.

    Requires an admissible PROPOSED MergeProposal AND caller authority
    covering both AUTHORIZE_MERGE and EXECUTE_MERGE (REQ-B3-045/046) —
    detection/assessment alone never suffices (REQ-B3-041).
    """
    authority.require(Authority.AUTHORIZE_MERGE, Authority.EXECUTE_MERGE)

    proposal = session.get(MergeProposal, proposal_id)
    if proposal is None:
        return OperationResult(outcome=OperationOutcome.NOT_FOUND, detail="merge proposal does not exist")

    source_id, target_id = proposal.source_contact_id, proposal.target_contact_id

    if source_id == target_id:
        return OperationResult(outcome=OperationOutcome.INVALID, detail="self-merge rejected")

    source = session.get(Contact, source_id)
    target = session.get(Contact, target_id)
    if source is None or target is None:
        return OperationResult(outcome=OperationOutcome.NOT_FOUND)

    # REQ-B3-052/071: idempotent replay of an already-completed merge.
    if source.contact_status == "MERGED":
        if source.merged_into_id == target_id:
            return OperationResult(outcome=OperationOutcome.ALREADY_MERGED, object_id=source_id)
        return OperationResult(outcome=OperationOutcome.CONFLICTING, detail="source already merged into a different target")

    if proposal.status not in ("PROPOSED", "AUTHORIZED"):
        return OperationResult(outcome=OperationOutcome.REJECTED, detail=f"proposal is not executable from status {proposal.status!r}")

    # REQ-B3-057..062: reconcile related objects BEFORE committing MERGED
    # state. Any conflict blocks the merge entirely (no partial merge).
    reject_reason = _reconcile_accounts(session, source_id, target_id)
    if reject_reason is None:
        reject_reason = _reconcile_contact_points(session, source_id, target_id)

    if reject_reason is not None:
        proposal.status = "REJECTED"
        proposal.resolved_at = datetime.now(timezone.utc)
        session.flush()
        record_operation(
            session,
            operation_type="MERGE_CONTACTS",
            decision="REJECT",
            result=OperationOutcome.CONFLICTING.value,
            actor_reference=authority.actor_reference,
            authority_context=authority.as_dict(),
            affected_object_ids=[str(source_id), str(target_id), str(proposal_id)],
        )
        return OperationResult(outcome=OperationOutcome.CONFLICTING, detail=reject_reason)

    # ContactAssetRelationships, CaseParticipants, ExternalReferences all
    # default to PRESERVE (REQ-B3-110..115) — deliberately untouched here;
    # they remain correctly attached to the historical source Contact.

    source.contact_status = "MERGED"
    source.merged_into_id = target_id
    source.updated_at = datetime.now(timezone.utc)
    source.record_version = (source.record_version or 0) + 1

    proposal.status = "EXECUTED"
    proposal.resolved_at = datetime.now(timezone.utc)
    session.flush()

    record_operation(
        session,
        operation_type="MERGE_CONTACTS",
        decision="EXECUTE",
        result=OperationOutcome.SUCCESS.value,
        actor_reference=authority.actor_reference,
        authority_context=authority.as_dict(),
        affected_object_ids=[str(source_id), str(target_id), str(proposal_id)],
    )
    return OperationResult(outcome=OperationOutcome.SUCCESS, object_id=target_id, payload={"source_contact_id": source_id})
