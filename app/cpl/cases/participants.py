"""CaseParticipant governance (REQ-B5-019..026, 077).

CaseParticipant is Case-scoped, distinct from ContactAssetRelationship
(REQ-B5-020). Being a participant never itself authorizes Case
mutation (REQ-B5-022) — this module never checks participant_role as
a substitute for AuthorityContext.
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
from app.cpl.models.case_participant import CaseParticipant
from app.cpl.models.canonical_case_decision import CanonicalCaseDecision
from app.cpl.models.case_mutation_request import CaseMutationRequest


def _idempotent_replay(session: Session, idempotency_key: str) -> Optional[CaseResult]:
    existing = session.get(CaseMutationRequest, idempotency_key)
    if existing is None:
        return None
    decision = session.get(CanonicalCaseDecision, existing.decision_id)
    return CaseResult(outcome=CaseOutcome.SUCCESS if decision.result == "EXECUTED" else CaseOutcome.NO_CHANGE,
                       object_id=decision.case_id, payload={"decision_id": decision.decision_id, "replay": True})


def add_participant(
    session: Session, *, case_id: UUID, contact_id: UUID, participant_role: str,
    authority: AuthorityContext, idempotency_key: str,
) -> CaseResult:
    authority.require(CaseAuthority.MANAGE_CASE_PARTICIPANT)

    replay = _idempotent_replay(session, idempotency_key)
    if replay is not None:
        return replay

    case = session.get(Case, case_id)
    contact = session.get(Contact, contact_id)
    if case is None or contact is None:
        return CaseResult(outcome=CaseOutcome.NOT_FOUND)

    participant = CaseParticipant(case_id=case_id, contact_id=contact_id,
                                    participant_role=participant_role, participant_status="ACTIVE")
    session.add(participant)
    session.flush()

    from app.cpl.cases.lifecycle import _record_decision, _record_idempotency
    decision = _record_decision(
        session, case_id=case_id, decision_type="PARTICIPANT_ADD", authority=authority,
        prior_value=None, new_value={"contact_id": str(contact_id), "participant_role": participant_role},
        result="EXECUTED",
    )
    _record_idempotency(session, idempotency_key, decision.decision_id)
    return CaseResult(outcome=CaseOutcome.SUCCESS, object_id=participant.case_participant_id,
                       payload={"decision_id": decision.decision_id})


def remove_participant(
    session: Session, *, case_participant_id: UUID, authority: AuthorityContext, idempotency_key: str,
) -> CaseResult:
    authority.require(CaseAuthority.MANAGE_CASE_PARTICIPANT)

    replay = _idempotent_replay(session, idempotency_key)
    if replay is not None:
        return replay

    participant = session.get(CaseParticipant, case_participant_id)
    if participant is None:
        return CaseResult(outcome=CaseOutcome.NOT_FOUND)
    if participant.participant_status != "ACTIVE":
        return CaseResult(outcome=CaseOutcome.NO_CHANGE, object_id=case_participant_id)

    prior_status = participant.participant_status
    participant.participant_status = "REMOVED"
    participant.left_at = datetime.now(timezone.utc)
    session.flush()

    from app.cpl.cases.lifecycle import _record_decision, _record_idempotency
    decision = _record_decision(
        session, case_id=participant.case_id, decision_type="PARTICIPANT_REMOVE", authority=authority,
        prior_value={"participant_status": prior_status}, new_value={"participant_status": "REMOVED"},
        result="EXECUTED",
    )
    _record_idempotency(session, idempotency_key, decision.decision_id)
    return CaseResult(outcome=CaseOutcome.SUCCESS, object_id=case_participant_id,
                       payload={"decision_id": decision.decision_id})


def can_participant_mutate_case(participant: CaseParticipant, authority: AuthorityContext) -> bool:
    """REQ-B5-022/023: structural proof that role alone never
    authorizes mutation — this helper deliberately ignores
    `participant.participant_role` entirely and defers 100% to
    AuthorityContext. Kept as a standalone function specifically so
    it can be unit-tested in isolation."""
    return CaseAuthority.TRANSITION_CASE_STATUS in authority.granted
