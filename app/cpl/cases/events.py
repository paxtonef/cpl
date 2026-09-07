"""CaseEvent recording and semantic classification (REQ-B5-027..038,
114..115).

CaseEvent is append-only (REQ-B5-034); recording a CaseEvent never
itself authorizes or constitutes a canonical decision (REQ-B5-030/031).
Semantic classification is definition-time (via CaseEventType), never
inferred from payload (REQ-B5-115).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.cpl.cases.authority import CaseAuthority, AuthorityContext
from app.cpl.cases.outcomes import CaseOutcome, CaseResult
from app.cpl.models.case import Case
from app.cpl.models.case_event import CaseEvent
from app.cpl.models.case_event_type import CaseEventType


def register_event_type(session: Session, *, event_type: str, semantic_class: str,
                         description: Optional[str] = None) -> CaseResult:
    """REQ-B5-115: a governed event_type MUST have a documented,
    determinable semantic class at definition time. This is a
    governance/setup operation, not a per-Case operation."""
    if semantic_class not in ("CPL_OPERATIONAL_FACT", "DOMAIN_ASSERTION",
                                "CANONICAL_DECISION_CONSEQUENCE", "TECHNICAL_SYSTEM_EVENT"):
        return CaseResult(outcome=CaseOutcome.SEMANTIC_REJECTION, detail="unrecognized semantic_class")
    existing = session.get(CaseEventType, event_type)
    if existing is not None:
        return CaseResult(outcome=CaseOutcome.NO_CHANGE, detail="event_type already registered")
    session.add(CaseEventType(event_type=event_type, semantic_class=semantic_class, description=description))
    session.flush()
    return CaseResult(outcome=CaseOutcome.SUCCESS)


def record_case_event(
    session: Session, *, case_id: UUID, event_type: str, actor_type: str,
    actor_reference_id: Optional[UUID] = None, execution_id: Optional[UUID] = None,
    payload: Optional[dict] = None, occurred_at: Optional[datetime] = None,
    authority: AuthorityContext,
) -> CaseResult:
    """REQ-B5-027/033/034: append-only recording. REQ-B5-035/036: the
    event_type MUST already be registered with a determinable semantic
    class — this function refuses to record an unregistered type
    rather than silently letting classification collapse. REQ-B5-114:
    occurred_at (reported/domain time) is preserved independently of
    created_at (CPL recording time, set automatically)."""
    authority.require(CaseAuthority.RECORD_CASE_EVENT)

    case = session.get(Case, case_id)
    if case is None:
        return CaseResult(outcome=CaseOutcome.NOT_FOUND, detail="case_id does not exist")

    event_type_def = session.get(CaseEventType, event_type)
    if event_type_def is None:
        # REQ-B5-035/036: governed event_type values only — no
        # arbitrary free-text type may be recorded.
        return CaseResult(outcome=CaseOutcome.SEMANTIC_REJECTION,
                           detail=f"event_type {event_type!r} is not registered with a semantic class")

    event = CaseEvent(
        case_id=case_id, event_type=event_type, actor_type=actor_type,
        actor_reference_id=actor_reference_id, execution_id=execution_id,
        occurred_at=occurred_at or datetime.now(timezone.utc), payload=payload, event_status="CURRENT",
    )
    session.add(event)
    session.flush()
    return CaseResult(outcome=CaseOutcome.SUCCESS, object_id=event.event_id,
                       payload={"semantic_class": event_type_def.semantic_class})


def correct_case_event(
    session: Session, *, event_id_to_correct: UUID, corrected_payload: Optional[dict],
    reason: str, authority: AuthorityContext, idempotency_key: str,
) -> CaseResult:
    """REQ-B5-071/072: correction by supersession, never destructive
    rewrite. The original CaseEvent row is preserved verbatim and
    marked SUPERSEDED; a new CURRENT event is created.

    R1: decision established BEFORE effect — the successor's PK is
    pre-generated so the decision can reference it before either the
    successor row or the prior-row supersession is applied.

    R3: a correction attempt against an event that is already
    SUPERSEDED is classified as CONFLICT, not SEMANTIC_REJECTION — two
    authoritative correction instructions targeting the same governed
    event are mutually incompatible (REQ-B5-082's own example), which
    is a materially different situation from a request that is simply
    invalid on its face."""
    authority.require(CaseAuthority.CORRECT_CASE)

    from app.cpl.models.canonical_case_decision import CanonicalCaseDecision
    from app.cpl.models.case_mutation_request import CaseMutationRequest
    existing_request = session.get(CaseMutationRequest, idempotency_key)
    if existing_request is not None:
        decision = session.get(CanonicalCaseDecision, existing_request.decision_id)
        outcome = CaseOutcome.SUCCESS if decision.result == "EXECUTED" else (decision.rejection_category or CaseOutcome.NO_CHANGE)
        return CaseResult(outcome=outcome, object_id=decision.result_object_id or decision.case_id,
                           payload={"decision_id": decision.decision_id, "replay": True})

    prior = session.get(CaseEvent, event_id_to_correct)
    if prior is None:
        return CaseResult(outcome=CaseOutcome.NOT_FOUND)
    if prior.event_status != "CURRENT":
        # R3: already-superseded target -> CONFLICT (two authoritative
        # correction instructions cannot both be honored), not a bare
        # SEMANTIC_REJECTION.
        from app.cpl.cases.lifecycle import _record_decision, _record_idempotency
        conflict_decision = _record_decision(
            session, case_id=prior.case_id, decision_type="EVENT_CORRECTION", authority=authority,
            prior_value={"event_id": str(prior.event_id), "event_status": prior.event_status},
            new_value={"attempted_payload": corrected_payload, "reason": reason},
            result="REJECTED", rejection_category=CaseOutcome.CONFLICT, result_object_id=prior.event_id,
        )
        _record_idempotency(session, idempotency_key, conflict_decision.decision_id)
        return CaseResult(outcome=CaseOutcome.CONFLICT, object_id=prior.event_id,
                           detail="event already superseded by a prior correction",
                           payload={"decision_id": conflict_decision.decision_id})

    from app.cpl.cases.lifecycle import _record_decision, _record_idempotency
    successor_id = uuid4()
    # R1: decision established BEFORE effect.
    decision = _record_decision(
        session, case_id=prior.case_id, decision_type="EVENT_CORRECTION", authority=authority,
        prior_value={"event_id": str(prior.event_id), "payload": prior.payload, "reason": reason},
        new_value={"event_id": str(successor_id), "payload": corrected_payload},
        result="EXECUTED", result_object_id=successor_id,
    )

    successor = CaseEvent(
        event_id=successor_id, case_id=prior.case_id, event_type=prior.event_type, actor_type=prior.actor_type,
        actor_reference_id=prior.actor_reference_id, execution_id=prior.execution_id,
        occurred_at=prior.occurred_at, payload=corrected_payload, event_status="CURRENT",
    )
    session.add(successor)
    session.flush()
    prior.event_status = "SUPERSEDED"
    prior.superseded_by_id = successor.event_id
    session.flush()

    _record_idempotency(session, idempotency_key, decision.decision_id)
    return CaseResult(outcome=CaseOutcome.SUCCESS, object_id=successor.event_id,
                       payload={"decision_id": decision.decision_id, "supersedes_event_id": prior.event_id})
