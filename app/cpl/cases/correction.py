"""Case metadata correction (REQ-B5-069, 072).

Correction preserves prior state via the CanonicalCaseDecision
ledger's prior_value/new_value JSONB rather than requiring new
per-field supersession columns on Case itself (GAP-03: schema kept
minimal, HOW left open).

Decision/effect ordering (R1 repair): the decision is established
BEFORE the Case row is mutated, not merely wrapped in the same
rollback-safe transaction.
"""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.cpl.cases.authority import CaseAuthority, AuthorityContext
from app.cpl.cases.outcomes import CaseOutcome, CaseResult
from app.cpl.models.case import Case
from app.cpl.models.canonical_case_decision import CanonicalCaseDecision
from app.cpl.models.case_mutation_request import CaseMutationRequest


def correct_case_metadata(
    session: Session, *, case_id: UUID, new_title: Optional[str] = None,
    new_case_type: Optional[str] = None, reason: str, authority: AuthorityContext,
    idempotency_key: str,
) -> CaseResult:
    """REQ-B5-069: correct title/case_type while preserving the prior
    value as reconstructable history in the decision ledger."""
    authority.require(CaseAuthority.CORRECT_CASE)

    existing_request = session.get(CaseMutationRequest, idempotency_key)
    if existing_request is not None:
        decision = session.get(CanonicalCaseDecision, existing_request.decision_id)
        return CaseResult(outcome=CaseOutcome.SUCCESS, object_id=decision.result_object_id or decision.case_id,
                           payload={"decision_id": decision.decision_id, "replay": True})

    case = session.get(Case, case_id)
    if case is None:
        return CaseResult(outcome=CaseOutcome.NOT_FOUND)

    prior_value = {"title": case.title, "case_type": case.case_type, "reason": reason}
    intended_new_value = {
        "title": new_title if new_title is not None else case.title,
        "case_type": new_case_type if new_case_type is not None else case.case_type,
    }

    from app.cpl.cases.lifecycle import _record_decision, _record_idempotency
    # R1: decision established BEFORE effect.
    decision = _record_decision(
        session, case_id=case_id, decision_type="METADATA_CORRECTION", authority=authority,
        prior_value=prior_value, new_value=intended_new_value, result="EXECUTED",
        result_object_id=case_id,
    )

    if new_title is not None:
        case.title = new_title
    if new_case_type is not None:
        case.case_type = new_case_type
    session.flush()

    _record_idempotency(session, idempotency_key, decision.decision_id)
    return CaseResult(outcome=CaseOutcome.SUCCESS, object_id=case_id,
                       payload={"decision_id": decision.decision_id})
