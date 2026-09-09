"""RunnerExecution admission and lifecycle (REQ-B6-001..023, 076, 077,
015, 088). Implements the frozen pipeline REQUEST -> AUTHORITY ->
DECISION -> EFFECT -> HISTORY for execution admission and status
transitions.

Two distinct transition entry points implement the repaired
REQ-B6-015/077 authority reconciliation:

  - `transition_status`         — decision_mode=AUTHORITY_EVALUATION.
                                   Operator/system-authority-driven
                                   transitions (QUEUED, RUNNING, BLOCKED,
                                   CANCELLED).
  - `persist_runner_report`     — decision_mode=AUTOMATIC_RULE_BOUND.
                                   The runner's self-reported COMPLETED/
                                   FAILED signal. Both paths still
                                   require the same base
                                   TRANSITION_EXECUTION_STATUS authority
                                   grant (REQ-B6-014: initiator/reporter
                                   is never itself sufficient authority)
                                   — what differs is that this path
                                   generates its decision record
                                   automatically, by rule, with no
                                   separate manual approval step, and
                                   that decision is marked
                                   AUTOMATIC_RULE_BOUND so it is
                                   distinguishable in the audit trail
                                   from an AUTHORITY_EVALUATION decision
                                   (REQ-B6-015's exact required
                                   distinction).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.cpl.runners.authority import RunnerAuthority, AuthorityContext, AuthorityDeniedError
from app.cpl.runners.idempotency import find_existing_by_key, compare_intent, IntentComparison
from app.cpl.runners.outcomes import RunnerOutcome, RunnerResult
from app.cpl.models.runner_execution import RunnerExecution
from app.cpl.models.runner_governance_decision import RunnerGovernanceDecision

# REQ-B6-009: the frozen minimum valid-transition table.
_TRANSITIONS = {
    "CREATED": {"QUEUED", "RUNNING", "BLOCKED", "CANCELLED", "FAILED"},
    "QUEUED": {"RUNNING", "BLOCKED", "CANCELLED", "FAILED"},
    "RUNNING": {"COMPLETED", "FAILED", "BLOCKED", "CANCELLED"},
    "BLOCKED": {"RUNNING", "CANCELLED", "FAILED"},
    "COMPLETED": set(),
    "FAILED": set(),
    "CANCELLED": set(),
}
_TERMINAL = {"COMPLETED", "FAILED", "CANCELLED"}
_RUNNER_REPORTED_STATUSES = {"COMPLETED", "FAILED"}  # REQ-B6-015's automatic-decision path


def admit_execution(
    session: Session,
    *,
    case_id: UUID,
    asset_id: UUID,
    runner_type: str,
    runner_version: str,
    execution_purpose: Optional[str] = None,
    initiated_by_contact_id: Optional[UUID] = None,
    idempotency_key: Optional[str] = None,
    authority: AuthorityContext,
) -> RunnerResult:
    """REQ-B6-076: execution admission requires a preceding governed
    authority decision; a rejected decision leaves no row (REQ-B6-009's
    "no row" case -> AUTHORITY_REJECTION). REQ-B6-035/036/037/088: the
    full idempotency contract, including the concurrent-insert race."""
    try:
        authority.require(RunnerAuthority.ADMIT_EXECUTION)
    except AuthorityDeniedError:
        return RunnerResult(outcome=RunnerOutcome.AUTHORITY_REJECTION, detail="missing ADMIT_EXECUTION authority")

    # REQ-B6-036/037: pre-check for an existing row under the same key.
    if idempotency_key is not None:
        existing = find_existing_by_key(session, runner_type=runner_type, idempotency_key=idempotency_key)
        if existing is not None:
            return _replay_or_conflict(existing, case_id=case_id, asset_id=asset_id, execution_purpose=execution_purpose)

    new_execution_id = uuid4()
    decision = RunnerGovernanceDecision(
        decision_type="EXECUTION_ADMISSION",
        decision_mode="AUTHORITY_EVALUATION",
        execution_id=new_execution_id,
        authority_context=authority.as_dict(),
        new_value={
            "case_id": str(case_id), "asset_id": str(asset_id), "runner_type": runner_type,
            "runner_version": runner_version, "execution_purpose": execution_purpose,
        },
        result="EXECUTED",
    )
    session.add(decision)

    execution = RunnerExecution(
        execution_id=new_execution_id, case_id=case_id, asset_id=asset_id, runner_type=runner_type,
        runner_version=runner_version, execution_purpose=execution_purpose,
        initiated_by_contact_id=initiated_by_contact_id, idempotency_key=idempotency_key,
        execution_status="CREATED",
    )
    session.add(execution)

    try:
        session.flush()
    except IntegrityError:
        # REQ-B6-088: concurrent-insert race on runner_executions_idempotency_uq.
        # The losing writer catches the violation and retrieves the winning
        # row, applying the same comparison — never a raw error to the caller.
        session.rollback()
        if idempotency_key is None:
            raise  # not an idempotency-key race; a genuine unexpected integrity failure
        existing = find_existing_by_key(session, runner_type=runner_type, idempotency_key=idempotency_key)
        if existing is None:
            raise  # race resolved to something else; do not silently swallow
        return _replay_or_conflict(existing, case_id=case_id, asset_id=asset_id, execution_purpose=execution_purpose)

    return RunnerResult(outcome=RunnerOutcome.SUCCESS, object_id=new_execution_id,
                         payload={"decision_id": decision.decision_id})


def _replay_or_conflict(
    existing: RunnerExecution, *, case_id: UUID, asset_id: UUID, execution_purpose: Optional[str],
) -> RunnerResult:
    comparison = compare_intent(existing, case_id=case_id, asset_id=asset_id, execution_purpose=execution_purpose)
    if comparison == IntentComparison.SAME_INTENT:
        # REQ-B6-036/REPLAY_OUTCOME_FIDELITY: retrieves the real existing row
        # (its actual identity/status), not a freshly constructed equivalent.
        return RunnerResult(outcome=RunnerOutcome.SUCCESS, object_id=existing.execution_id,
                             payload={"replay": True})
    return RunnerResult(outcome=RunnerOutcome.CONFLICT, object_id=existing.execution_id,
                         detail="idempotency_key reused with a materially different governed operation")


def transition_status(
    session: Session, *, execution_id: UUID, new_status: str, authority: AuthorityContext,
) -> RunnerResult:
    """REQ-B6-077, 009, 010: operator/system-authority-driven transition.
    AUTHORITY_EVALUATION decision mode."""
    return _apply_transition(session, execution_id=execution_id, new_status=new_status, authority=authority,
                              decision_mode="AUTHORITY_EVALUATION")


def persist_runner_report(
    session: Session, *, execution_id: UUID, new_status: str, authority: AuthorityContext,
) -> RunnerResult:
    """REQ-B6-015 (repaired), 077: the runner's self-reported COMPLETED/
    FAILED signal. Satisfies REQ-B6-077's decision-record requirement via
    an automatic, rule-bound decision — not a bypass of it. Carries no
    domain-truth weight (REQ-B6-007/EA-CI03): COMPLETED means only that
    the runner reported finishing."""
    if new_status not in _RUNNER_REPORTED_STATUSES:
        raise ValueError(f"{new_status!r} is not a runner-reportable status; use transition_status instead")
    return _apply_transition(session, execution_id=execution_id, new_status=new_status, authority=authority,
                              decision_mode="AUTOMATIC_RULE_BOUND")


def _apply_transition(
    session: Session, *, execution_id: UUID, new_status: str, authority: AuthorityContext, decision_mode: str,
) -> RunnerResult:
    try:
        authority.require(RunnerAuthority.TRANSITION_EXECUTION_STATUS)
    except AuthorityDeniedError:
        return RunnerResult(outcome=RunnerOutcome.AUTHORITY_REJECTION, detail="missing TRANSITION_EXECUTION_STATUS authority")

    execution = session.get(RunnerExecution, execution_id)
    if execution is None:
        return RunnerResult(outcome=RunnerOutcome.NOT_FOUND)

    prior_status = execution.execution_status

    # REQ-B6-010: repeated transition request to the current value is an
    # idempotent no-op — success, no state change, no new decision record.
    if prior_status == new_status:
        return RunnerResult(outcome=RunnerOutcome.SUCCESS, object_id=execution_id, payload={"no_op": True})

    if new_status not in _TRANSITIONS.get(prior_status, set()):
        # REQ-B6-012 analogue at the transition-table level: an
        # unauthorized transition attempt is a SEMANTIC_REJECTION, never
        # silently accepted and never a technical exception.
        return RunnerResult(outcome=RunnerOutcome.SEMANTIC_REJECTION, object_id=execution_id,
                             detail=f"{prior_status} -> {new_status} is not a valid transition")

    decision = RunnerGovernanceDecision(
        decision_type="EXECUTION_STATUS_TRANSITION",
        decision_mode=decision_mode,
        execution_id=execution_id,
        authority_context=authority.as_dict(),
        prior_value={"execution_status": prior_status},
        new_value={"execution_status": new_status},
        result="EXECUTED",
    )
    session.add(decision)

    execution.execution_status = new_status
    now = datetime.now(timezone.utc)
    if new_status == "RUNNING" and execution.started_at is None:
        execution.started_at = now
    if new_status == "COMPLETED":
        # REQ-B6-013: runner_executions_completed_at_chk preserved.
        execution.completed_at = now
    session.flush()

    return RunnerResult(outcome=RunnerOutcome.SUCCESS, object_id=execution_id,
                         payload={"decision_id": decision.decision_id})


def retry_execution(
    session: Session,
    *,
    case_id: UUID,
    asset_id: UUID,
    runner_type: str,
    runner_version: str,
    execution_purpose: Optional[str] = None,
    initiated_by_contact_id: Optional[UUID] = None,
    idempotency_key: Optional[str] = None,
    authority: AuthorityContext,
) -> RunnerResult:
    """REQ-B6-004/040: a genuine retry is simply a new admission — no
    special code path, no use of `parent_execution_id` (REQ-B6-006/043).
    If `idempotency_key` reuses the failed attempt's key, `admit_execution`
    governs it identically to any other duplicate submission (REQ-B6-040)."""
    return admit_execution(
        session, case_id=case_id, asset_id=asset_id, runner_type=runner_type, runner_version=runner_version,
        execution_purpose=execution_purpose, initiated_by_contact_id=initiated_by_contact_id,
        idempotency_key=idempotency_key, authority=authority,
    )
