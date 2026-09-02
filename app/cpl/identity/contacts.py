"""Primitives 01-03: get_contact, resolve_contact, create_contact."""
from __future__ import annotations

from typing import Iterable, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.cpl.identity.authority import Authority, AuthorityContext
from app.cpl.identity.evidence import Evidence
from app.cpl.identity.outcomes import OperationOutcome, OperationResult, ResolutionResult, ResolutionState
from app.cpl.identity.provenance import record_operation
from app.cpl.identity.resolution import resolve_contact as _resolve_contact
from app.cpl.models.contact import Contact
from app.cpl.models.contact_creation_request import ContactCreationRequest

_VALID_CONTACT_TYPES = {"PERSON", "ORGANIZATION"}


def get_contact(session: Session, contact_id: UUID, authority: Optional[AuthorityContext] = None) -> OperationResult:
    """Primitive 01 (REQ-B3-001..003). Pure retrieval, no mutation."""
    if authority is not None:
        authority.require(Authority.READ_IDENTITY)

    contact = session.get(Contact, contact_id)
    if contact is None:
        return OperationResult(outcome=OperationOutcome.NOT_FOUND)
    return OperationResult(outcome=OperationOutcome.SUCCESS, object_id=contact.contact_id, payload={"contact": contact})


def resolve_contact(session: Session, evidence: Iterable[Evidence], authority: Optional[AuthorityContext] = None) -> ResolutionResult:
    """Primitive 02 (REQ-B3-004..011). Pure resolution, no mutation."""
    if authority is not None:
        authority.require(Authority.RESOLVE_IDENTITY)
    return _resolve_contact(session, evidence)


def create_contact(
    session: Session,
    *,
    contact_type: str,
    display_name: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    authority: AuthorityContext,
    idempotency_key: Optional[str] = None,
) -> OperationResult:
    """Primitive 03 (REQ-B3-012..016, 067, 072, 124/125).

    Creation does not implicitly establish verification, Account
    binding, or any other identity-bearing relationship
    (REQ-B3-014).
    """
    authority.require(Authority.CREATE_CONTACT)

    if contact_type not in _VALID_CONTACT_TYPES:
        return OperationResult(outcome=OperationOutcome.INVALID, detail=f"unsupported contact_type: {contact_type!r}")

    # REQ-B3-124/125: same governed idempotency_key => same logical creation.
    # Similarity of name/etc alone is explicitly NOT sufficient (REQ-B3-125).
    if idempotency_key is not None:
        existing = session.get(ContactCreationRequest, idempotency_key)
        if existing is not None:
            return OperationResult(
                outcome=OperationOutcome.SUCCESS,
                object_id=existing.contact_id,
                payload={"replayed": True},
            )

    contact = Contact(
        contact_type=contact_type,
        display_name=display_name,
        first_name=first_name,
        last_name=last_name,
        contact_status="ACTIVE",
    )
    session.add(contact)
    session.flush()

    if idempotency_key is not None:
        session.add(ContactCreationRequest(idempotency_key=idempotency_key, contact_id=contact.contact_id))
        session.flush()

    record_operation(
        session,
        operation_type="CREATE_CONTACT",
        decision="CREATE_CONTACT",
        result=OperationOutcome.SUCCESS.value,
        actor_reference=authority.actor_reference,
        authority_context=authority.as_dict(),
        affected_object_ids=[str(contact.contact_id)],
    )

    return OperationResult(outcome=OperationOutcome.SUCCESS, object_id=contact.contact_id, payload={"replayed": False})
