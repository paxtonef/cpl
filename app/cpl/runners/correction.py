"""RunnerExecution metadata correction (REQ-B6-062..065).

Append-only: never mutates historical field values in place on
`runner_executions` itself for the corrected field's prior value (the
prior value is preserved only in the correction log row); the current
value on `runner_executions` reflects the correction, but the log makes
the original value reconstructable (REQ-B6-064/065 history
reconstructability). Only non-occurrence metadata may be corrected here
— `execution_status` and identity fields are explicitly out of scope
for this function (REQ-B6-062: a historical occurrence must never be
rewritten as if a different execution happened)."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.cpl.runners.authority import RunnerAuthority, AuthorityContext, AuthorityDeniedError
from app.cpl.runners.outcomes import RunnerOutcome, RunnerResult
from app.cpl.models.runner_execution import RunnerExecution
from app.cpl.models.runner_execution_correction import RunnerExecutionCorrection

# REQ-B6-062: execution_status and identity fields are never correctable
# through this path — only non-occurrence metadata.
_CORRECTABLE_FIELDS = frozenset({"execution_purpose", "runner_version"})


def correct_execution_metadata(
    session: Session, *, execution_id: UUID, field_name: str, new_value: Any, authority: AuthorityContext,
) -> RunnerResult:
    try:
        authority.require(RunnerAuthority.CORRECT_EXECUTION)
    except AuthorityDeniedError:
        return RunnerResult(outcome=RunnerOutcome.AUTHORITY_REJECTION, detail="missing CORRECT_EXECUTION authority")

    if field_name not in _CORRECTABLE_FIELDS:
        return RunnerResult(outcome=RunnerOutcome.SEMANTIC_REJECTION,
                             detail=f"{field_name!r} is not a correctable non-occurrence field")

    execution = session.get(RunnerExecution, execution_id)
    if execution is None:
        return RunnerResult(outcome=RunnerOutcome.NOT_FOUND)

    prior_value = getattr(execution, field_name)
    if prior_value == new_value:
        return RunnerResult(outcome=RunnerOutcome.NO_CHANGE, object_id=execution_id)

    correction = RunnerExecutionCorrection(
        execution_id=execution_id, corrected_field=field_name, prior_value={"value": prior_value},
        new_value={"value": new_value}, authority_context=authority.as_dict(),
    )
    session.add(correction)
    setattr(execution, field_name, new_value)
    session.flush()

    return RunnerResult(outcome=RunnerOutcome.SUCCESS, object_id=execution_id,
                         payload={"correction_id": correction.correction_id})


def reconstruct_original_value(session: Session, *, execution_id: UUID, field_name: str) -> Any:
    """REQ-B6-065 history reconstructability: returns the earliest
    recorded prior_value for the given field, i.e. the value before any
    correction — or the current live value if no correction was ever
    recorded for this field."""
    earliest = (
        session.query(RunnerExecutionCorrection)
        .filter(RunnerExecutionCorrection.execution_id == execution_id, RunnerExecutionCorrection.corrected_field == field_name)
        .order_by(RunnerExecutionCorrection.corrected_at.asc())
        .first()
    )
    if earliest is not None:
        return earliest.prior_value["value"]
    execution = session.get(RunnerExecution, execution_id)
    return getattr(execution, field_name) if execution is not None else None
