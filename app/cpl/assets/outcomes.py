"""B4 outcome vocabulary (REQ-B4-162..171, F19).

Extends the B3 OperationOutcome/OperationResult envelope (reused as-is)
with the additional semantic outcomes required for Asset/relationship
identity governance: AMBIGUOUS, CONTRADICTORY, UNRESOLVED, HOLD are
governed non-resolution states, kept strictly distinct from technical
FAILED (REQ-B4-170/171) — a resolver crash or DB timeout is never
silently reported as a domain outcome.
"""
from __future__ import annotations

from app.cpl.identity.outcomes import OperationOutcome, OperationResult

# Additional B4 outcome values, added to the shared enum-like vocabulary.
# OperationOutcome is a str Enum; B4 code uses these string constants
# directly in OperationResult(outcome=...) rather than mutating the B3
# enum, preserving B3 non-regression while extending observable outcomes.


class B4Outcome:
    AMBIGUOUS = "AMBIGUOUS"
    CONTRADICTORY = "CONTRADICTORY"
    UNRESOLVED = "UNRESOLVED"
    HOLD = "HOLD"
    FAILED = "FAILED"


class TechnicalFailureError(Exception):
    """Raised only for genuine technical execution failure (REQ-B4-032,
    REQ-B4-054, REQ-B4-170). MUST NOT be raised for legitimate governed
    non-resolution outcomes (AMBIGUOUS/CONTRADICTORY/UNRESOLVED/HOLD) —
    those are typed results, exactly mirroring the B3
    IdentityOperationError discipline."""


__all__ = ["OperationOutcome", "OperationResult", "B4Outcome", "TechnicalFailureError"]
