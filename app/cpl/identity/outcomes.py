"""Shared semantic outcome vocabulary for B3 identity operations.

Implements the outcome distinctions required by REQ-B3-090 through
REQ-B3-094 (RMO-20) and the resolution-state vocabulary from
B3_IDENTITY_RESOLUTION_STATE_DECISION_MODEL_v0.md Section 4.

These are semantic outcome classes, not HTTP status codes or
exception hierarchies — the transport-layer mapping is deliberately
left open (frozen WHAT boundary, see WHAT Freeze Sec. 42).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
from uuid import UUID


class ResolutionState(str, Enum):
    """Identity Resolution State & Decision Model v0, Section 4."""

    MATCHED = "MATCHED"
    NOT_FOUND = "NOT_FOUND"
    AMBIGUOUS = "AMBIGUOUS"
    CONFLICTING = "CONFLICTING"
    UNRESOLVED = "UNRESOLVED"
    PROVISIONAL = "PROVISIONAL"


class OperationOutcome(str, Enum):
    """RMO-20 semantic outcome vocabulary (REQ-B3-090..094)."""

    SUCCESS = "SUCCESS"
    NOT_FOUND = "NOT_FOUND"
    REJECTED = "REJECTED"
    INVALID = "INVALID"
    CONFLICTING = "CONFLICTING"
    ALREADY_EXISTS = "ALREADY_EXISTS"
    ALREADY_MERGED = "ALREADY_MERGED"
    NO_CHANGE = "NO_CHANGE"
    EXECUTION_FAILURE = "EXECUTION_FAILURE"


class IdentityOperationError(Exception):
    """Raised only for genuine execution failure (REQ-B3-011, REQ-B3-090).

    MUST NOT be raised for legitimate domain outcomes such as
    NOT_FOUND, AMBIGUOUS, CONFLICTING, UNRESOLVED, REJECTED — those
    are represented as typed results, not exceptions, precisely so
    that a technical failure is never confused with an epistemic
    identity conclusion.
    """


@dataclass
class ResolutionResult:
    """Result of resolve_contact / resolve_authenticated_contact."""

    state: ResolutionState
    contact_id: Optional[UUID] = None
    candidate_contact_ids: list[UUID] = field(default_factory=list)
    reason: Optional[str] = None


@dataclass
class OperationResult:
    """Common result envelope (Service Boundary v0.1 Section 5)."""

    outcome: OperationOutcome
    object_id: Optional[UUID] = None
    resolution: Optional[ResolutionResult] = None
    detail: Optional[str] = None
    payload: dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.outcome in (OperationOutcome.SUCCESS, OperationOutcome.NO_CHANGE, OperationOutcome.ALREADY_MERGED)
