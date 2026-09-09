"""B6 Execution/Artifact Governance outcome vocabulary (REQ-B6-066,
repaired). Implements the explicit five-category disposition the
repaired requirement establishes: AUTHORITY_REJECTION maps to the
pre-materialization "no row" case (REQ-B6-076); SEMANTIC_REJECTION maps
to artifact REJECTED (REQ-B6-033, structural reason only, never domain);
UNRESOLVED maps to execution BLOCKED (REQ-B6-012); CONFLICT maps to the
idempotency conflict outcome (REQ-B6-037); TECHNICAL_FAILURE is never
conflated with any of the above (REQ-B6-066/067). Domain rejection is
explicitly unrepresentable in this vocabulary (REQ-B6-060/067)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional
from uuid import UUID


class RunnerOutcome:
    SUCCESS = "SUCCESS"
    NOT_FOUND = "NOT_FOUND"
    NO_CHANGE = "NO_CHANGE"
    AUTHORITY_REJECTION = "AUTHORITY_REJECTION"
    SEMANTIC_REJECTION = "SEMANTIC_REJECTION"
    UNRESOLVED = "UNRESOLVED"
    CONFLICT = "CONFLICT"
    TECHNICAL_FAILURE = "TECHNICAL_FAILURE"


@dataclass
class RunnerResult:
    outcome: str
    object_id: Optional[UUID] = None
    detail: Optional[str] = None
    payload: dict = field(default_factory=dict)


class RunnerTechnicalFailureError(Exception):
    """Raised only for genuine technical execution failure. MUST NOT be
    raised for legitimate governed outcomes (UNRESOLVED/CONFLICT/
    SEMANTIC_REJECTION/AUTHORITY_REJECTION) — those are typed results,
    never exceptions (REQ-B6-066/068)."""
