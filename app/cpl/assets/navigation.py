"""Historical attribution vs current canonical navigation
(REQ-B4-255..260, RM-B4-04).

The Asset/ContactAssetRelationship/ExternalReference tables already
preserve the *historical* row exactly as originally recorded — no B4
code ever rewrites relationship.asset_id / relationship.contact_id or
external_reference targets in place. These helpers provide the
*current* view by walking the merge-successor chain, so both
properties (REQ-B4-255/256/258/259) are independently reconstructable
from the same stored facts.
"""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.cpl.models.asset import Asset
from app.cpl.models.contact import Contact


def current_asset_id(session: Session, asset_id: UUID) -> UUID:
    """Resolve an Asset's current canonical successor, following the
    merged_into_id chain. Returns the historical asset_id unchanged if
    it was never merged (REQ-B4-255, REQ-B4-257)."""
    seen: set[UUID] = set()
    current = asset_id
    while True:
        if current in seen:
            # Defensive: a cycle would indicate corrupted governance
            # data, never a legitimate canonical state.
            return current
        seen.add(current)
        asset = session.get(Asset, current)
        if asset is None or asset.merged_into_id is None:
            return current
        current = asset.merged_into_id


def current_contact_id(session: Session, contact_id: UUID) -> UUID:
    """Mirror of current_asset_id for B3 Contact canonical successors
    (REQ-B4-256, cross-B3 compatibility F22)."""
    seen: set[UUID] = set()
    current = contact_id
    while True:
        if current in seen:
            return current
        seen.add(current)
        contact = session.get(Contact, current)
        if contact is None or contact.merged_into_id is None:
            return current
        current = contact.merged_into_id


def relationship_current_view(session: Session, relationship) -> dict:
    """REQ-B4-257/258: current canonical navigation resolves through
    successors without rewriting the historical endpoints stored on
    `relationship` itself."""
    return {
        "relationship_id": relationship.relationship_id,
        "historical_contact_id": relationship.contact_id,
        "historical_asset_id": relationship.asset_id,
        "current_contact_id": current_contact_id(session, relationship.contact_id),
        "current_asset_id": current_asset_id(session, relationship.asset_id),
    }


def external_reference_current_view(session: Session, external_reference) -> dict:
    """REQ-B4-259: historical CPL target preserved verbatim; current
    navigation resolves through the Asset merge-successor chain only
    when entity_type == 'asset'."""
    historical_target = external_reference.entity_id
    if external_reference.entity_type == "asset":
        current_target = current_asset_id(session, historical_target)
    else:
        current_target = historical_target
    return {
        "external_reference_id": external_reference.external_reference_id,
        "historical_target": historical_target,
        "current_target": current_target,
    }
