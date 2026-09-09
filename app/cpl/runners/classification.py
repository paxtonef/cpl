"""Artifact classification (REQ-B6-026..028, 090).

Three orthogonal dimensions, each independently settable, none forcing
exclusivity with the others (EA-CI05/19). All three are mandatory at
registration (REQ-B6-090); `validate_classification` distinguishes the
five outcomes the frozen requirement names explicitly: INVALID_VALUE,
UNSUPPORTED_VALUE, CONTRADICTORY_COMBINATION (currently unreachable by
design — no combination is defined mutually exclusive, confirmed, not
silently ignored), MISSING_REQUIRED_DIMENSION, VALID."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

SEMANTIC_FUNCTION_VALUES = frozenset({
    "EXECUTION_OUTPUT_CARRIER",
    "EXECUTION_EVIDENCE_CARRIER",
    "DOMAIN_ASSERTION_CARRIER",
    "DOMAIN_DETERMINATION_CARRIER",
    "TECHNICAL_OPERATIONAL_MATERIAL",
})
LIFECYCLE_ROLE_VALUES = frozenset({"INTERMEDIATE", "FINAL"})
PRESENTATION_ROLE_VALUES = frozenset({"INTERNAL", "PRODUCT_DISPLAYABLE"})


class ClassificationValidationOutcome:
    VALID = "VALID"
    INVALID_VALUE = "INVALID_VALUE"
    UNSUPPORTED_VALUE = "UNSUPPORTED_VALUE"
    CONTRADICTORY_COMBINATION = "CONTRADICTORY_COMBINATION"
    MISSING_REQUIRED_DIMENSION = "MISSING_REQUIRED_DIMENSION"


@dataclass
class ClassificationValidationResult:
    outcome: str
    detail: Optional[str] = None


def validate_classification(
    *, semantic_function: Optional[str], lifecycle_role: Optional[str], presentation_role: Optional[str],
) -> ClassificationValidationResult:
    """REQ-B6-090: registration-time validation. No two of the five
    outcomes may collapse into the same observable result — each branch
    below returns a distinct, unambiguous outcome."""
    if semantic_function is None or lifecycle_role is None or presentation_role is None:
        missing = [
            name for name, value in (
                ("semantic_function", semantic_function),
                ("lifecycle_role", lifecycle_role),
                ("presentation_role", presentation_role),
            ) if value is None
        ]
        return ClassificationValidationResult(
            outcome=ClassificationValidationOutcome.MISSING_REQUIRED_DIMENSION,
            detail=f"missing dimension(s): {', '.join(missing)}",
        )

    if semantic_function not in SEMANTIC_FUNCTION_VALUES:
        return ClassificationValidationResult(
            outcome=ClassificationValidationOutcome.INVALID_VALUE,
            detail=f"semantic_function {semantic_function!r} is not in the defined vocabulary",
        )
    if lifecycle_role not in LIFECYCLE_ROLE_VALUES:
        return ClassificationValidationResult(
            outcome=ClassificationValidationOutcome.INVALID_VALUE,
            detail=f"lifecycle_role {lifecycle_role!r} is not in the defined vocabulary",
        )
    if presentation_role not in PRESENTATION_ROLE_VALUES:
        return ClassificationValidationResult(
            outcome=ClassificationValidationOutcome.INVALID_VALUE,
            detail=f"presentation_role {presentation_role!r} is not in the defined vocabulary",
        )

    # REQ-B6-026: no combination is currently defined mutually exclusive.
    # This branch is structurally unreachable today — confirmed, not
    # silently omitted (see REQ-B6-090's own Notes on this point).
    # UNSUPPORTED_VALUE is likewise not currently reachable: every value
    # in the three vocabularies above is fully supported by this Build
    # Unit at this time; the outcome exists in the taxonomy for values a
    # future WHAT/Requirements amendment might add to a vocabulary
    # before the corresponding implementation support lands.

    return ClassificationValidationResult(outcome=ClassificationValidationOutcome.VALID)
