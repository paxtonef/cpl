"""RunnerExecution idempotency contract (REQ-B6-035..042, 088).

Scope is exactly (runner_type, idempotency_key), matching the existing
enforced constraint `runner_executions_idempotency_uq` (REQ-B6-035) —
this module does not widen or narrow that scope. `idempotency_key` is
never treated as RunnerExecution identity (REQ-B6-003/041; EA-CI16/18)
— it is a lookup key only, never used in place of `execution_id`.
"""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.cpl.models.runner_execution import RunnerExecution


class IntentComparison:
    SAME_INTENT = "SAME_INTENT"
    CONFLICT = "CONFLICT"


def find_existing_by_key(session: Session, *, runner_type: str, idempotency_key: str) -> Optional[RunnerExecution]:
    """REQ-B6-035: exact enforced scope, (runner_type, idempotency_key)."""
    if idempotency_key is None:
        # REQ-B6-039: NULL key never deduplicates.
        return None
    return (
        session.query(RunnerExecution)
        .filter(RunnerExecution.runner_type == runner_type, RunnerExecution.idempotency_key == idempotency_key)
        .one_or_none()
    )


def compare_intent(
    existing: RunnerExecution, *, case_id: UUID, asset_id: UUID, execution_purpose: Optional[str],
) -> str:
    """REQ-B6-038: the exact, minimum defensible comparison set —
    case_id, asset_id, execution_purpose. Request payload content beyond
    these fields is explicitly NOT part of this comparison (payload is
    opaque, matching the identity-independence discipline elsewhere in
    this Build Unit)."""
    if (
        existing.case_id == case_id
        and existing.asset_id == asset_id
        and existing.execution_purpose == execution_purpose
    ):
        return IntentComparison.SAME_INTENT
    return IntentComparison.CONFLICT
