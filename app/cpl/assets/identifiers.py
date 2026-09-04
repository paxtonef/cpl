"""AssetIdentifier governed lifecycle (REQ-B4-015..024, F03).

Identifier equality never independently establishes SAME_PHYSICAL_ASSET
(REQ-B4-022) — there is deliberately no function here that merges
Assets from matching identifier values; only app.cpl.assets.merge,
gated on a governed AssetIdentityResolution, can do that (REQ-B4-047).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.cpl.assets.authority import AssetAuthority, AuthorityContext
from app.cpl.assets.outcomes import OperationOutcome, OperationResult
from app.cpl.models.asset import Asset
from app.cpl.models.asset_identifier import AssetIdentifier


def add_asset_identifier(
    session: Session, *, asset_id: UUID, identifier_type: str, identifier_value: str,
    normalized_value: Optional[str] = None, country: Optional[str] = None, source: Optional[str] = None,
    confidence: Optional[float] = None, authority: AuthorityContext,
) -> OperationResult:
    """REQ-B4-015..017: attach, retaining type/provenance."""
    authority.require(AssetAuthority.MANAGE_ASSET_IDENTIFIER)

    asset = session.get(Asset, asset_id)
    if asset is None:
        return OperationResult(outcome=OperationOutcome.NOT_FOUND)

    identifier = AssetIdentifier(
        asset_id=asset_id, identifier_type=identifier_type, identifier_value=identifier_value,
        normalized_value=normalized_value, country=country, source=source, confidence=confidence,
        identifier_status="OBSERVED", valid_from=datetime.now(timezone.utc),
    )
    session.add(identifier)
    session.flush()
    return OperationResult(outcome=OperationOutcome.SUCCESS, object_id=identifier.asset_identifier_id)


def verify_asset_identifier(session: Session, *, asset_identifier_id: UUID, authority: AuthorityContext) -> OperationResult:
    authority.require(AssetAuthority.MANAGE_ASSET_IDENTIFIER)
    identifier = session.get(AssetIdentifier, asset_identifier_id)
    if identifier is None:
        return OperationResult(outcome=OperationOutcome.NOT_FOUND)
    identifier.identifier_status = "VERIFIED"
    session.flush()
    return OperationResult(outcome=OperationOutcome.SUCCESS, object_id=identifier.asset_identifier_id)


def supersede_asset_identifier(
    session: Session, *, asset_identifier_id: UUID, new_identifier_value: str,
    new_normalized_value: Optional[str], authority: AuthorityContext,
) -> OperationResult:
    """REQ-B4-019/021/037: identifier replacement preserves historical
    attribution — the prior row is retained with SUPERSEDED status,
    never overwritten in place (REQ-B4-005/006: Asset continuity
    across mutable identifier change is unaffected)."""
    authority.require(AssetAuthority.MANAGE_ASSET_IDENTIFIER)

    prior = session.get(AssetIdentifier, asset_identifier_id)
    if prior is None:
        return OperationResult(outcome=OperationOutcome.NOT_FOUND)
    if prior.identifier_status in ("SUPERSEDED", "INVALIDATED"):
        return OperationResult(outcome=OperationOutcome.INVALID, detail=f"identifier already {prior.identifier_status}")

    successor = AssetIdentifier(
        asset_id=prior.asset_id, identifier_type=prior.identifier_type, identifier_value=new_identifier_value,
        normalized_value=new_normalized_value, country=prior.country, source=prior.source,
        identifier_status="OBSERVED", valid_from=datetime.now(timezone.utc),
    )
    session.add(successor)
    session.flush()

    prior.identifier_status = "SUPERSEDED"
    prior.valid_until = datetime.now(timezone.utc)
    session.flush()
    return OperationResult(outcome=OperationOutcome.SUCCESS, object_id=successor.asset_identifier_id,
                            payload={"supersedes": prior.asset_identifier_id})


def invalidate_asset_identifier(session: Session, *, asset_identifier_id: UUID, authority: AuthorityContext) -> OperationResult:
    """REQ-B4-020: identifier invalidation. REQ-B4-005: MUST NOT, by
    itself, invalidate the Asset — no Asset field is touched here."""
    authority.require(AssetAuthority.MANAGE_ASSET_IDENTIFIER)
    identifier = session.get(AssetIdentifier, asset_identifier_id)
    if identifier is None:
        return OperationResult(outcome=OperationOutcome.NOT_FOUND)
    identifier.identifier_status = "INVALIDATED"
    identifier.valid_until = identifier.valid_until or datetime.now(timezone.utc)
    session.flush()
    return OperationResult(outcome=OperationOutcome.SUCCESS, object_id=identifier.asset_identifier_id)


def dispute_asset_identifier(session: Session, *, asset_identifier_id: UUID, authority: AuthorityContext) -> OperationResult:
    """REQ-B4-024: conflicting identifier evidence becomes DISPUTED
    (governed non-resolution), never silently deleted or reassigned."""
    authority.require(AssetAuthority.MANAGE_ASSET_IDENTIFIER)
    identifier = session.get(AssetIdentifier, asset_identifier_id)
    if identifier is None:
        return OperationResult(outcome=OperationOutcome.NOT_FOUND)
    identifier.identifier_status = "DISPUTED"
    session.flush()
    return OperationResult(outcome=OperationOutcome.SUCCESS, object_id=identifier.asset_identifier_id)


def get_asset_identifiers(session: Session, asset_id: UUID, *, include_historical: bool = True) -> list[AssetIdentifier]:
    """REQ-B4-021: historically applicable identifiers remain
    retrievable after replacement/invalidation unless the caller
    explicitly restricts to current-only."""
    stmt = select(AssetIdentifier).where(AssetIdentifier.asset_id == asset_id)
    if not include_historical:
        stmt = stmt.where(AssetIdentifier.identifier_status.in_(("OBSERVED", "VERIFIED")))
    return list(session.execute(stmt).scalars().all())


def find_assets_by_identifier_value(session: Session, identifier_value: str) -> list[UUID]:
    """REQ-B4-022/023: identifier match returns candidate Assets as
    *evidence only* — this function performs no merge, no resolution,
    and no canonical mutation of any kind. Callers feeding this into a
    domain resolver's evidence set remain responsible for keeping that
    distinction (identifier match != identity determination)."""
    stmt = select(AssetIdentifier.asset_id).where(AssetIdentifier.identifier_value == identifier_value)
    return sorted({row[0] for row in session.execute(stmt).all()}, key=str)
