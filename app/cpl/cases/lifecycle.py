"""Case creation and lifecycle status transitions (REQ-B5-001..018,
039..051, 075..079, 109..113).

Implements the frozen pipeline: REQUEST -> AUTHORITY -> DECISION ->
EFFECT -> HISTORY (REQ-B5-047, 110, 111, 112). Case.asset_id remains
NOT NULL and is never mutated after creation (REQ-B5-109) — there is
no update-asset_id code path at all; `attempt_asset_rebind` exists
only to make the prohibition itself independently testable and
auditable via a recorded decision (REQ-B5-080's SEMANTIC_REJECTION
example).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.cpl.cases.authority import CaseAuthority, AuthorityContext
from app.cpl.cases.outcomes import CaseOutcome, CaseResult
from app.cpl.models.case import Case
from app.cpl.models.contact import Contact
from app.cpl.models.asset import Asset
from app.cpl.models.canonical_case_decision import CanonicalCaseDecision
from app.cpl.models.case_mutation_request import CaseMutationRequest

VALID_CASE_STATUSES = frozenset({
    "OPEN", "IN_PROGRESS", "WAITING_FOR_USER", "WAITING_FOR_EXTERNAL_INFORMATION",
    "RESOLVED", "CLOSED", "REOPENED", "CANCELLED",
})


def _idempotent_replay(session: Session, idempotency_key: str) -> Optional[CaseResult]:
    existing = session.get(CaseMutationRequest, idempotency_key)
    if existing is None:
        return None
    decision = session.get(CanonicalCaseDecision, existing.decision_id)
    outcome = CaseOutcome.SUCCESS if decision.result == "EXECUTED" else (
        decision.rejection_category or CaseOutcome.NO_CHANGE
    )
    return CaseResult(outcome=outcome, object_id=decision.case_id,
                       payload={"decision_id": decision.decision_id, "replay": True})


def create_case(
    session: Session, *, primary_contact_id: UUID, asset_id: UUID, domain: str, case_type: str,
    title: Optional[str] = None, authority: AuthorityContext, idempotency_key: str,
) -> CaseResult:
    """REQ-B5-011/014/018: requires an existing Contact and a
    canonically valid Asset. REQ-B5-012: no implicit creation from
    elsewhere. REQ-B5-075: idempotent by governed request identity."""
    authority.require(CaseAuthority.CREATE_CASE)

    replay = _idempotent_replay(session, idempotency_key)
    if replay is not None:
        return replay

    contact = session.get(Contact, primary_contact_id)
    if contact is None:
        return CaseResult(outcome=CaseOutcome.NOT_FOUND, detail="primary_contact_id does not exist")
    asset = session.get(Asset, asset_id)
    if asset is None or asset.asset_status == "MERGED":
        return CaseResult(outcome=CaseOutcome.NOT_FOUND, detail="asset_id is not a canonically valid Asset")

    case = Case(primary_contact_id=primary_contact_id, asset_id=asset_id, domain=domain,
                case_type=case_type, case_status="OPEN", title=title)
    session.add(case)
    session.flush()

    decision = _record_decision(
        session, case_id=case.case_id, decision_type="CREATE", authority=authority,
        prior_value=None, new_value={"case_status": "OPEN"}, result="EXECUTED",
    )
    _record_idempotency(session, idempotency_key, decision.decision_id)
    return CaseResult(outcome=CaseOutcome.SUCCESS, object_id=case.case_id,
                       payload={"decision_id": decision.decision_id})


def transition_case_status(
    session: Session, *, case_id: UUID, new_status: str, authority: AuthorityContext,
    idempotency_key: str,
) -> CaseResult:
    """REQ-B5-039..045, 047, 110..112: governed status transition.
    REQ-B5-040/041: no domain-truth-laden statuses accepted or implied
    by this function — it only ever writes the frozen enum values."""
    authority.require(CaseAuthority.TRANSITION_CASE_STATUS)

    replay = _idempotent_replay(session, idempotency_key)
    if replay is not None:
        return replay

    if new_status not in VALID_CASE_STATUSES:
        # REQ-B5-041: never accept/introduce a domain-truth-laden status.
        return CaseResult(outcome=CaseOutcome.SEMANTIC_REJECTION, detail=f"{new_status!r} is not a governed Case status")

    case = session.get(Case, case_id)
    if case is None:
        return CaseResult(outcome=CaseOutcome.NOT_FOUND)

    prior_status = case.case_status
    if prior_status == new_status:
        return CaseResult(outcome=CaseOutcome.NO_CHANGE, object_id=case_id)

    # REQ-B5-110: decision established before effect. REQ-B5-112: if
    # anything below raises, the whole session rolls back — no partial
    # transition (decision without effect, or effect without decision)
    # is ever committed, satisfying REQ-B5-047's pipeline invariant.
    decision = _record_decision(
        session, case_id=case_id, decision_type="STATUS_TRANSITION", authority=authority,
        prior_value={"case_status": prior_status}, new_value={"case_status": new_status}, result="EXECUTED",
    )
    case.case_status = new_status
    case.updated_at = datetime.now(timezone.utc)
    case.record_version = (case.record_version or 0) + 1
    if new_status == "CLOSED":
        case.closed_at = datetime.now(timezone.utc)
    session.flush()

    _record_idempotency(session, idempotency_key, decision.decision_id)
    return CaseResult(outcome=CaseOutcome.SUCCESS, object_id=case_id,
                       payload={"decision_id": decision.decision_id})  # REQ-B5-111: decision row is the trace/history


def attempt_asset_rebind(
    session: Session, *, case_id: UUID, new_asset_id: UUID, authority: AuthorityContext,
    idempotency_key: str,
) -> CaseResult:
    """REQ-B5-109: post-creation Asset rebinding is prohibited under
    B5. This function exists so the prohibition is independently
    testable/auditable (a recorded, governed rejection), not merely
    an absence of an update code path. It NEVER mutates Case.asset_id."""
    authority.require(CaseAuthority.TRANSITION_CASE_STATUS)

    replay = _idempotent_replay(session, idempotency_key)
    if replay is not None:
        return replay

    case = session.get(Case, case_id)
    if case is None:
        return CaseResult(outcome=CaseOutcome.NOT_FOUND)

    decision = _record_decision(
        session, case_id=case_id, decision_type="ASSET_REBIND_ATTEMPT", authority=authority,
        prior_value={"asset_id": str(case.asset_id)}, new_value={"attempted_asset_id": str(new_asset_id)},
        result="REJECTED", rejection_category=CaseOutcome.SEMANTIC_REJECTION,
    )
    _record_idempotency(session, idempotency_key, decision.decision_id)
    return CaseResult(outcome=CaseOutcome.SEMANTIC_REJECTION, object_id=case_id,
                       detail="post-creation Asset rebinding is prohibited under B5 Case Governance",
                       payload={"decision_id": decision.decision_id})


def _record_decision(session: Session, *, case_id: UUID, decision_type: str, authority: AuthorityContext,
                      prior_value: Optional[dict], new_value: Optional[dict], result: str,
                      rejection_category: Optional[str] = None,
                      supersedes: Optional[UUID] = None) -> CanonicalCaseDecision:
    decision = CanonicalCaseDecision(
        case_id=case_id, decision_type=decision_type, authority_context=authority.as_dict(),
        prior_value=prior_value, new_value=new_value, result=result,
        rejection_category=rejection_category, supersedes_decision_id=supersedes,
    )
    session.add(decision)
    session.flush()
    return decision


def _record_idempotency(session: Session, idempotency_key: str, decision_id: UUID) -> None:
    session.add(CaseMutationRequest(idempotency_key=idempotency_key, decision_id=decision_id))
    session.flush()
