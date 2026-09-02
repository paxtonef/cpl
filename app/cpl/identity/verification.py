"""Verification Assertion minimum contract (REQ-B3-116..120).

B3 does not perform external verification (email/SMS/OTP/OAuth
challenge/etc) — it consumes the RESULT of such a mechanism as an
admissible assertion (F-B3-04). This module defines only the
minimum semantic shape required to make an admissibility decision.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class VerificationAssertion:
    """REQ-B3-116: minimum recoverable assertion semantics."""

    contact_point_id: UUID
    verification_class: str
    issuer: str
    result: str  # "ACCEPTED" | "REJECTED" from the external mechanism's perspective
    verified_at: datetime
    authority_context: Optional[dict] = None
    replay_key: Optional[str] = None
    expires_at: Optional[datetime] = None


class AssertionRejected(Exception):
    """Raised when a Verification Assertion fails admissibility (REQ-B3-118).

    This is a legitimate domain rejection, not an execution failure
    — callers translate it into their own outcome representation.
    """


def check_admissible(assertion: VerificationAssertion, expected_contact_point_id: UUID) -> None:
    """REQ-B3-118: reject on target mismatch, negative result, expiry,
    or missing mandatory provenance. Raises AssertionRejected with a
    specific reason; does not silently pass anything through.
    """
    if assertion.contact_point_id != expected_contact_point_id:
        raise AssertionRejected("assertion target does not match the ContactPoint being verified")

    if assertion.result != "ACCEPTED":
        raise AssertionRejected(f"verification result was not accepted: {assertion.result!r}")

    if not assertion.issuer:
        raise AssertionRejected("assertion missing mandatory issuer/source provenance")

    if assertion.expires_at is not None and assertion.expires_at < datetime.now(timezone.utc):
        raise AssertionRejected("assertion has expired")
