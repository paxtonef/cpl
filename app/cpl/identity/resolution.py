"""Canonical B3 identity resolution engine.

One resolution semantics for all evidence types (F-B3-05).
Resolution never mutates identity state (REQ-B3-004, B3-SB-I03).

Design notes (HOW-level, not frozen semantics):
  - Evidence is partitioned into STRONG (VERIFIED ContactPoint,
    ACTIVE Account binding) and WEAK (UNVERIFIED ContactPoint).
  - Only ACTIVE Accounts contribute resolution authority (F-B3-06,
    REQ-B3-033..036) — PENDING/DISABLED/REVOKED never do.
  - A resolved Contact that is itself MERGED is transparently
    followed to its surviving target (bounded chain, cycle-safe).
  - Multiple STRONG evidence items disagreeing on distinct surviving
    Contacts => CONFLICTING (REQ-B3-008).
  - Multiple distinct candidate Contacts with no single agreed
    conclusion, none of them CONFLICTING => AMBIGUOUS (REQ-B3-007).
  - No evidence resolves to any Contact => NOT_FOUND (REQ-B3-006).
"""
from __future__ import annotations

from typing import Iterable, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.cpl.identity.evidence import EmailEvidence, Evidence, PhoneEvidence, ProviderAccountEvidence
from app.cpl.identity.outcomes import ResolutionResult, ResolutionState
from app.cpl.models.account import Account
from app.cpl.models.contact import Contact
from app.cpl.models.contact_point import ContactPoint

_MAX_MERGE_CHAIN_HOPS = 50


def _follow_merge_chain(session: Session, contact_id: UUID) -> Optional[UUID]:
    """Follow Contact.merged_into_id to the surviving Contact.

    Returns None if the chain is broken (dangling reference) or
    exceeds a bounded hop count (cycle protection) rather than
    looping forever.
    """
    seen: set[UUID] = set()
    current = contact_id
    for _ in range(_MAX_MERGE_CHAIN_HOPS):
        if current in seen:
            return None
        seen.add(current)
        contact = session.get(Contact, current)
        if contact is None:
            return None
        if contact.contact_status != "MERGED" or contact.merged_into_id is None:
            return current
        current = contact.merged_into_id
    return None


def _normalize_email(value: str) -> str:
    return value.strip().lower()


def _normalize_phone(value: str) -> str:
    return "".join(ch for ch in value if ch.isdigit() or ch == "+")


def _candidates_for_evidence(session: Session, item: Evidence) -> tuple[set[UUID], bool]:
    """Return (candidate surviving contact_ids, is_strong) for one evidence item."""
    if isinstance(item, EmailEvidence):
        normalized = _normalize_email(item.value)
        rows = session.execute(
            select(ContactPoint).where(
                ContactPoint.point_type == "EMAIL",
                ContactPoint.normalized_value == normalized,
                ContactPoint.valid_until.is_(None),
            )
        ).scalars().all()
        strong = any(r.verification_status == "VERIFIED" for r in rows)
        ids = {_follow_merge_chain(session, r.contact_id) for r in rows}
        return {i for i in ids if i is not None}, strong

    if isinstance(item, PhoneEvidence):
        normalized = _normalize_phone(item.value)
        rows = session.execute(
            select(ContactPoint).where(
                ContactPoint.point_type == "PHONE",
                ContactPoint.normalized_value == normalized,
                ContactPoint.valid_until.is_(None),
            )
        ).scalars().all()
        strong = any(r.verification_status == "VERIFIED" for r in rows)
        ids = {_follow_merge_chain(session, r.contact_id) for r in rows}
        return {i for i in ids if i is not None}, strong

    if isinstance(item, ProviderAccountEvidence):
        # F-B3-06 / REQ-B3-033..036: only ACTIVE bindings resolve current identity.
        row = session.execute(
            select(Account).where(
                Account.auth_provider == item.provider,
                Account.provider_subject_id == item.provider_subject,
                Account.account_status == "ACTIVE",
            )
        ).scalar_one_or_none()
        if row is None:
            return set(), False
        resolved = _follow_merge_chain(session, row.contact_id)
        return ({resolved} if resolved else set()), True

    raise TypeError(f"Unsupported evidence type: {type(item)!r}")


def resolve_contact(session: Session, evidence: Iterable[Evidence]) -> ResolutionResult:
    """Canonical resolution entry point (REQ-B3-004..011).

    Pure read/assessment — MUST NOT mutate any identity state.
    """
    evidence = list(evidence)
    if not evidence:
        return ResolutionResult(state=ResolutionState.UNRESOLVED, reason="no evidence supplied")

    strong_candidates: set[UUID] = set()
    all_candidates: set[UUID] = set()
    for item in evidence:
        ids, is_strong = _candidates_for_evidence(session, item)
        all_candidates |= ids
        if is_strong:
            strong_candidates |= ids

    if not all_candidates:
        return ResolutionResult(state=ResolutionState.NOT_FOUND)

    if len(all_candidates) == 1:
        return ResolutionResult(state=ResolutionState.MATCHED, contact_id=next(iter(all_candidates)))

    # More than one distinct surviving Contact implicated.
    if len(strong_candidates) > 1:
        return ResolutionResult(
            state=ResolutionState.CONFLICTING,
            candidate_contact_ids=sorted(strong_candidates, key=str),
            reason="multiple strong evidence items disagree on surviving Contact",
        )

    return ResolutionResult(
        state=ResolutionState.AMBIGUOUS,
        candidate_contact_ids=sorted(all_candidates, key=str),
        reason="multiple plausible Contacts, no admissible rule selects one",
    )


def resolve_authenticated_contact(
    session: Session, provider: str, provider_subject: str, extra_evidence: Iterable[Evidence] = ()
) -> ResolutionResult:
    """Specialized resolution entry point (REQ-B3-033..036).

    Uses the SAME canonical resolution engine as resolve_contact
    (F-B3-05) — authenticated provider identity is one evidence
    type among others, not a second resolution ontology.
    """
    evidence = [ProviderAccountEvidence(provider=provider, provider_subject=provider_subject), *extra_evidence]
    return resolve_contact(session, evidence)
