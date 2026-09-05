"""ExternalReference lifecycle: add / supersede / invalidate
(REQ-B4-087..095, F10).

Historical target preservation is structural, not a lifecycle-state
concern: entity_id is never rewritten in place after Asset merge
(see app.cpl.assets.navigation.external_reference_current_view for
the current-navigation projection). This module governs the
reference's own lifecycle (CURRENT/SUPERSEDED/INVALIDATED).
"""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.cpl.assets.authority import AssetAuthority, AuthorityContext
from app.cpl.assets.outcomes import OperationOutcome, OperationResult
from app.cpl.models.external_reference import ExternalReference


def add_external_reference(
    session: Session, *, entity_type: str, entity_id: UUID, reference_system: str,
    reference_type: str, reference_value: str, authority: AuthorityContext,
) -> OperationResult:
    authority.require(AssetAuthority.CONSUME_IDENTITY_RESOLUTION)
    ref = ExternalReference(
        entity_type=entity_type, entity_id=entity_id, reference_system=reference_system,
        reference_type=reference_type, reference_value=reference_value, reference_status="CURRENT",
    )
    session.add(ref)
    session.flush()
    return OperationResult(outcome=OperationOutcome.SUCCESS, object_id=ref.external_reference_id)


def supersede_external_reference(
    session: Session, *, external_reference_id: UUID, new_reference_value: str, authority: AuthorityContext,
) -> OperationResult:
    """REQ-B4-093: supersession without erasing historical provenance —
    the prior row remains, marked SUPERSEDED, pointing to its successor."""
    authority.require(AssetAuthority.CONSUME_IDENTITY_RESOLUTION)

    prior = session.get(ExternalReference, external_reference_id)
    if prior is None:
        return OperationResult(outcome=OperationOutcome.NOT_FOUND)
    if prior.reference_status != "CURRENT":
        return OperationResult(outcome=OperationOutcome.INVALID, detail="only a CURRENT reference may be superseded")

    successor = ExternalReference(
        entity_type=prior.entity_type, entity_id=prior.entity_id, reference_system=prior.reference_system,
        reference_type=prior.reference_type, reference_value=new_reference_value, reference_status="CURRENT",
    )
    session.add(successor)
    session.flush()
    prior.reference_status = "SUPERSEDED"
    prior.superseded_by_id = successor.external_reference_id
    session.flush()
    return OperationResult(outcome=OperationOutcome.SUCCESS, object_id=successor.external_reference_id,
                            payload={"supersedes": prior.external_reference_id})


def invalidate_external_reference(session: Session, *, external_reference_id: UUID, authority: AuthorityContext) -> OperationResult:
    authority.require(AssetAuthority.CONSUME_IDENTITY_RESOLUTION)
    ref = session.get(ExternalReference, external_reference_id)
    if ref is None:
        return OperationResult(outcome=OperationOutcome.NOT_FOUND)
    ref.reference_status = "INVALIDATED"
    session.flush()
    return OperationResult(outcome=OperationOutcome.SUCCESS, object_id=ref.external_reference_id)
