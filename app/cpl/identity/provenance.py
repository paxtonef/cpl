"""Durable provenance recording (REQ-B3-076..079, REQ-B3-121..123)."""
from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.cpl.models.identity_operation import IdentityOperation


def record_operation(
    session: Session,
    *,
    operation_type: str,
    decision: str,
    result: str,
    actor_reference: Optional[str] = None,
    authority_context: Optional[dict[str, Any]] = None,
    evidence_reference: Optional[dict[str, Any]] = None,
    affected_object_ids: Optional[list[str]] = None,
) -> IdentityOperation:
    """Record durable provenance for a material B3 operation.

    MUST be called for every operation that mutates identity state
    (REQ-B3-076). MUST NOT be used to fabricate provenance that
    doesn't exist (REQ-B3-079) — callers pass only what they
    genuinely know.
    """
    op = IdentityOperation(
        operation_type=operation_type,
        actor_reference=actor_reference,
        authority_context=authority_context,
        evidence_reference=evidence_reference,
        affected_object_ids=affected_object_ids or [],
        decision=decision,
        result=result,
    )
    session.add(op)
    session.flush()
    return op
