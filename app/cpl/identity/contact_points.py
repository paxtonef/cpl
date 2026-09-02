"""Primitives 04-07: add_contact_point, verify_contact_point,
invalidate_contact_point, set_primary_contact_point.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.cpl.identity.authority import Authority, AuthorityContext
from app.cpl.identity.outcomes import OperationOutcome, OperationResult
from app.cpl.identity.provenance import record_operation
from app.cpl.identity.verification import AssertionRejected, VerificationAssertion, check_admissible
from app.cpl.models.contact import Contact
from app.cpl.models.contact_point import ContactPoint
from app.cpl.models.contact_point_verification import ContactPointVerification

_VALID_POINT_TYPES = {"EMAIL", "PHONE"}


def _normalize(point_type: str, value: str) -> str:
    if point_type == "EMAIL":
        return value.strip().lower()
    return re.sub(r"[^\d+]", "", value)


def add_contact_point(
    session: Session,
    *,
    contact_id: UUID,
    point_type: str,
    raw_value: str,
    authority: AuthorityContext,
    is_primary: bool = False,
) -> OperationResult:
    """Primitive 04 (REQ-B3-017..019). Does NOT imply verification (REQ-B3-018)."""
    authority.require(Authority.MANAGE_CONTACT_POINT)

    if point_type not in _VALID_POINT_TYPES:
        return OperationResult(outcome=OperationOutcome.INVALID, detail=f"unsupported point_type: {point_type!r}")

    contact = session.get(Contact, contact_id)
    if contact is None:
        return OperationResult(outcome=OperationOutcome.NOT_FOUND, detail="Contact does not exist")

    point = ContactPoint(
        contact_id=contact_id,
        point_type=point_type,
        raw_value=raw_value,
        normalized_value=_normalize(point_type, raw_value),
        verification_status="UNVERIFIED",
        is_primary=is_primary,
    )
    session.add(point)
    try:
        session.flush()
    except IntegrityError:
        session.rollback()
        return OperationResult(outcome=OperationOutcome.CONFLICTING, detail="primary ContactPoint conflict")

    record_operation(
        session,
        operation_type="ADD_CONTACT_POINT",
        decision="ADD_CONTACT_POINT",
        result=OperationOutcome.SUCCESS.value,
        actor_reference=authority.actor_reference,
        authority_context=authority.as_dict(),
        affected_object_ids=[str(point.contact_point_id)],
    )
    return OperationResult(outcome=OperationOutcome.SUCCESS, object_id=point.contact_point_id)


def verify_contact_point(
    session: Session, *, assertion: VerificationAssertion, authority: AuthorityContext
) -> OperationResult:
    """Primitive 05 (REQ-B3-023..027, 116..120).

    Requires an admissible VerificationAssertion — a caller
    declaration alone is never sufficient (REQ-B3-024, REQ-B3-120).
    """
    authority.require(Authority.VERIFY_CONTACT_POINT)

    point = session.get(ContactPoint, assertion.contact_point_id)
    if point is None:
        return OperationResult(outcome=OperationOutcome.NOT_FOUND, detail="ContactPoint does not exist")

    # REQ-B3-027 replay safety: same (point, class, replay_key) already recorded => idempotent success.
    if assertion.replay_key is not None:
        existing = session.execute(
            select(ContactPointVerification).where(
                ContactPointVerification.contact_point_id == assertion.contact_point_id,
                ContactPointVerification.verification_class == assertion.verification_class,
                ContactPointVerification.replay_key == assertion.replay_key,
            )
        ).scalar_one_or_none()
        if existing is not None:
            return OperationResult(outcome=OperationOutcome.SUCCESS, object_id=point.contact_point_id, payload={"replayed": True})

    try:
        check_admissible(assertion, expected_contact_point_id=point.contact_point_id)
    except AssertionRejected as exc:
        session.add(ContactPointVerification(
            contact_point_id=assertion.contact_point_id,
            verification_class=assertion.verification_class,
            issuer=assertion.issuer or "unknown",
            result="REJECTED",
            verified_at=assertion.verified_at,
            expires_at=assertion.expires_at,
            authority_context=assertion.authority_context,
            replay_key=assertion.replay_key,
        ))
        session.flush()
        return OperationResult(outcome=OperationOutcome.REJECTED, detail=str(exc))

    session.add(ContactPointVerification(
        contact_point_id=assertion.contact_point_id,
        verification_class=assertion.verification_class,
        issuer=assertion.issuer,
        result="ACCEPTED",
        verified_at=assertion.verified_at,
        expires_at=assertion.expires_at,
        authority_context=assertion.authority_context,
        replay_key=assertion.replay_key,
    ))
    point.verification_status = "VERIFIED"
    point.updated_at = datetime.now(timezone.utc)
    session.flush()

    record_operation(
        session,
        operation_type="VERIFY_CONTACT_POINT",
        decision="ACCEPT_VERIFICATION",
        result=OperationOutcome.SUCCESS.value,
        actor_reference=authority.actor_reference,
        authority_context=authority.as_dict(),
        evidence_reference={"verification_class": assertion.verification_class, "issuer": assertion.issuer},
        affected_object_ids=[str(point.contact_point_id)],
    )
    return OperationResult(outcome=OperationOutcome.SUCCESS, object_id=point.contact_point_id, payload={"replayed": False})


def invalidate_contact_point(
    session: Session, *, contact_point_id: UUID, authority: AuthorityContext
) -> OperationResult:
    """Primitive 06 (REQ-B3-020). Preserves history — no physical delete."""
    authority.require(Authority.MANAGE_CONTACT_POINT)

    point = session.get(ContactPoint, contact_point_id)
    if point is None:
        return OperationResult(outcome=OperationOutcome.NOT_FOUND)

    if point.valid_until is not None:
        return OperationResult(outcome=OperationOutcome.NO_CHANGE, object_id=point.contact_point_id)

    point.valid_until = datetime.now(timezone.utc)
    point.updated_at = datetime.now(timezone.utc)
    session.flush()

    record_operation(
        session,
        operation_type="INVALIDATE_CONTACT_POINT",
        decision="INVALIDATE",
        result=OperationOutcome.SUCCESS.value,
        actor_reference=authority.actor_reference,
        authority_context=authority.as_dict(),
        affected_object_ids=[str(point.contact_point_id)],
    )
    return OperationResult(outcome=OperationOutcome.SUCCESS, object_id=point.contact_point_id)


def set_primary_contact_point(
    session: Session, *, contact_point_id: UUID, authority: AuthorityContext
) -> OperationResult:
    """Primitive 07 (REQ-B3-021..022). Primary = preferred current point,
    NOT identity authority.
    """
    authority.require(Authority.MANAGE_CONTACT_POINT)

    point = session.get(ContactPoint, contact_point_id)
    if point is None:
        return OperationResult(outcome=OperationOutcome.NOT_FOUND)
    if point.valid_until is not None:
        return OperationResult(outcome=OperationOutcome.REJECTED, detail="cannot make an inactive ContactPoint primary")

    # Demote any other active primary of the same type first (avoids
    # transient unique-index violation within the same transaction).
    siblings = session.execute(
        select(ContactPoint).where(
            ContactPoint.contact_id == point.contact_id,
            ContactPoint.point_type == point.point_type,
            ContactPoint.is_primary.is_(True),
            ContactPoint.valid_until.is_(None),
            ContactPoint.contact_point_id != point.contact_point_id,
        )
    ).scalars().all()
    for sib in siblings:
        sib.is_primary = False
    session.flush()

    point.is_primary = True
    point.updated_at = datetime.now(timezone.utc)
    try:
        session.flush()
    except IntegrityError:
        session.rollback()
        return OperationResult(outcome=OperationOutcome.CONFLICTING, detail="primary ContactPoint conflict")

    record_operation(
        session,
        operation_type="SET_PRIMARY_CONTACT_POINT",
        decision="SET_PRIMARY",
        result=OperationOutcome.SUCCESS.value,
        actor_reference=authority.actor_reference,
        authority_context=authority.as_dict(),
        affected_object_ids=[str(point.contact_point_id)],
    )
    return OperationResult(outcome=OperationOutcome.SUCCESS, object_id=point.contact_point_id)
