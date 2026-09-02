"""Primitives 08-11: attach_account, resolve_authenticated_contact,
disable_account, revoke_account.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.cpl.identity.authority import Authority, AuthorityContext
from app.cpl.identity.evidence import Evidence
from app.cpl.identity.outcomes import OperationOutcome, OperationResult, ResolutionResult
from app.cpl.identity.provenance import record_operation
from app.cpl.identity.resolution import resolve_authenticated_contact as _resolve_authenticated_contact
from app.cpl.models.account import Account
from app.cpl.models.contact import Contact


def attach_account(
    session: Session,
    *,
    contact_id: UUID,
    auth_provider: str,
    provider_subject_id: str,
    authority: AuthorityContext,
) -> OperationResult:
    """Primitive 08 (REQ-B3-028..032). Provider identity does not
    become CPL identity authority (REQ-B3-032)."""
    authority.require(Authority.ATTACH_ACCOUNT)

    contact = session.get(Contact, contact_id)
    if contact is None:
        return OperationResult(outcome=OperationOutcome.NOT_FOUND, detail="Contact does not exist")

    existing = session.execute(
        select(Account).where(
            Account.auth_provider == auth_provider,
            Account.provider_subject_id == provider_subject_id,
        )
    ).scalar_one_or_none()

    if existing is not None:
        if existing.contact_id == contact_id:
            return OperationResult(outcome=OperationOutcome.ALREADY_EXISTS, object_id=existing.account_id)
        # REQ-B3-030: contradictory existing binding => CONFLICTING, never silent rebind.
        return OperationResult(
            outcome=OperationOutcome.CONFLICTING,
            detail="provider identity already bound to a different Contact",
        )

    account = Account(
        contact_id=contact_id,
        auth_provider=auth_provider,
        provider_subject_id=provider_subject_id,
        account_status="ACTIVE",
    )
    session.add(account)
    try:
        session.flush()
    except IntegrityError:
        session.rollback()
        return OperationResult(outcome=OperationOutcome.CONFLICTING, detail="concurrent duplicate provider binding")

    record_operation(
        session,
        operation_type="ATTACH_ACCOUNT",
        decision="ATTACH_ACCOUNT",
        result=OperationOutcome.SUCCESS.value,
        actor_reference=authority.actor_reference,
        authority_context=authority.as_dict(),
        affected_object_ids=[str(account.account_id), str(contact_id)],
    )
    return OperationResult(outcome=OperationOutcome.SUCCESS, object_id=account.account_id)


def resolve_authenticated_contact(
    session: Session,
    *,
    provider: str,
    provider_subject: str,
    authority: AuthorityContext,
    extra_evidence: Iterable[Evidence] = (),
) -> ResolutionResult:
    """Primitive 09 (REQ-B3-033..036). Same resolution engine as
    resolve_contact (F-B3-05) — does not itself create/mutate."""
    authority.require(Authority.RESOLVE_IDENTITY)
    return _resolve_authenticated_contact(session, provider, provider_subject, extra_evidence)


def disable_account(session: Session, *, account_id: UUID, authority: AuthorityContext) -> OperationResult:
    """Primitive 10 (REQ-B3-037). Historical binding preserved (not deleted)."""
    authority.require(Authority.MANAGE_ACCOUNT)

    account = session.get(Account, account_id)
    if account is None:
        return OperationResult(outcome=OperationOutcome.NOT_FOUND)
    if account.account_status == "DISABLED":
        return OperationResult(outcome=OperationOutcome.NO_CHANGE, object_id=account.account_id)
    if account.account_status == "REVOKED":
        return OperationResult(outcome=OperationOutcome.REJECTED, detail="cannot disable a revoked Account")

    account.account_status = "DISABLED"
    account.disabled_at = datetime.now(timezone.utc)
    session.flush()

    record_operation(
        session,
        operation_type="DISABLE_ACCOUNT",
        decision="DISABLE",
        result=OperationOutcome.SUCCESS.value,
        actor_reference=authority.actor_reference,
        authority_context=authority.as_dict(),
        affected_object_ids=[str(account.account_id)],
    )
    return OperationResult(outcome=OperationOutcome.SUCCESS, object_id=account.account_id)


def revoke_account(session: Session, *, account_id: UUID, authority: AuthorityContext) -> OperationResult:
    """Primitive 11 (REQ-B3-038). Historical binding preserved (not deleted)."""
    authority.require(Authority.MANAGE_ACCOUNT)

    account = session.get(Account, account_id)
    if account is None:
        return OperationResult(outcome=OperationOutcome.NOT_FOUND)
    if account.account_status == "REVOKED":
        return OperationResult(outcome=OperationOutcome.NO_CHANGE, object_id=account.account_id)

    account.account_status = "REVOKED"
    session.flush()

    record_operation(
        session,
        operation_type="REVOKE_ACCOUNT",
        decision="REVOKE",
        result=OperationOutcome.SUCCESS.value,
        actor_reference=authority.actor_reference,
        authority_context=authority.as_dict(),
        affected_object_ids=[str(account.account_id)],
    )
    return OperationResult(outcome=OperationOutcome.SUCCESS, object_id=account.account_id)
