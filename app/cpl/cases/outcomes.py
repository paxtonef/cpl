"""B5 Case Governance outcome vocabulary (REQ-B5-080..084).

Five governed outcome categories, kept strictly distinct:
AUTHORITY_REJECTION, SEMANTIC_REJECTION, UNRESOLVED, CONFLICT are
governed non-resolution/rejection states; TECHNICAL_FAILURE is never
conflated with any of them (a DB timeout is never silently reported
as a governed rejection).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional
from uuid import UUID


class CaseOutcome:
    SUCCESS = "SUCCESS"
    NOT_FOUND = "NOT_FOUND"
    NO_CHANGE = "NO_CHANGE"
    AUTHORITY_REJECTION = "AUTHORITY_REJECTION"
    SEMANTIC_REJECTION = "SEMANTIC_REJECTION"
    UNRESOLVED = "UNRESOLVED"
    CONFLICT = "CONFLICT"
    TECHNICAL_FAILURE = "TECHNICAL_FAILURE"


@dataclass
class CaseResult:
    outcome: str
    object_id: Optional[UUID] = None
    detail: Optional[str] = None
    payload: dict = field(default_factory=dict)


class CaseTechnicalFailureError(Exception):
    """Raised only for genuine technical execution failure (REQ-B5-083).
    MUST NOT be raised for legitimate governed outcomes (UNRESOLVED/
    CONFLICT/SEMANTIC_REJECTION/AUTHORITY_REJECTION) — those are typed
    results, never exceptions."""
