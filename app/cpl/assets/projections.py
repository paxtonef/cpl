"""DomainProjection lifecycle: attach / supersede / conflict-aware read
(REQ-B4-096..103, F11).

Generic CPL governs attachment/continuity/history; it never adjudicates
conflicting domain truth (REQ-B4-101) — where two CURRENT projections
of the same type conflict, callers get DOMAIN_RECONCILIATION_REQUIRED
and may choose to HOLD any dependent Asset merge (REQ-B4-102).
"""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.cpl.assets.authority import AssetAuthority, AuthorityContext
from app.cpl.assets.outcomes import OperationOutcome, OperationResult
from app.cpl.models.asset import Asset
from app.cpl.models.domain_projection import DomainProjection


def attach_domain_projection(
    session: Session, *, asset_id: UUID, projection_type: str, payload: Optional[dict],
    domain_authority: Optional[str], source_resolution_id: Optional[UUID],
    authority: AuthorityContext,
) -> OperationResult:
    authority.require(AssetAuthority.CONSUME_IDENTITY_RESOLUTION)

    asset = session.get(Asset, asset_id)
    if asset is None:
        return OperationResult(outcome=OperationOutcome.NOT_FOUND)

    projection = DomainProjection(
        asset_id=asset_id, projection_type=projection_type, projection_status="CURRENT",
        payload=payload, domain_authority=domain_authority, source_resolution_id=source_resolution_id,
    )
    session.add(projection)
    session.flush()
    return OperationResult(outcome=OperationOutcome.SUCCESS, object_id=projection.projection_id)


def supersede_domain_projection(
    session: Session, *, projection_id: UUID, new_payload: Optional[dict],
    domain_authority: Optional[str], source_resolution_id: Optional[UUID],
    authority: AuthorityContext,
) -> OperationResult:
    """REQ-B4-100: update/supersession while preserving required
    history — the prior row is marked SUPERSEDED, never overwritten
    in place or deleted."""
    authority.require(AssetAuthority.CONSUME_IDENTITY_RESOLUTION)

    prior = session.get(DomainProjection, projection_id)
    if prior is None:
        return OperationResult(outcome=OperationOutcome.NOT_FOUND)
    if prior.projection_status != "CURRENT":
        return OperationResult(outcome=OperationOutcome.INVALID, detail="only a CURRENT projection may be superseded")

    new_projection = DomainProjection(
        asset_id=prior.asset_id, projection_type=prior.projection_type, projection_status="CURRENT",
        payload=new_payload, domain_authority=domain_authority, source_resolution_id=source_resolution_id,
        supersedes_projection_id=prior.projection_id,
    )
    prior.projection_status = "SUPERSEDED"
    session.add(new_projection)
    session.flush()
    return OperationResult(outcome=OperationOutcome.SUCCESS, object_id=new_projection.projection_id,
                            payload={"supersedes_projection_id": prior.projection_id})


def current_projections_for_asset(session: Session, asset_id: UUID, projection_type: Optional[str] = None) -> list[DomainProjection]:
    stmt = select(DomainProjection).where(DomainProjection.asset_id == asset_id, DomainProjection.projection_status == "CURRENT")
    if projection_type is not None:
        stmt = stmt.where(DomainProjection.projection_type == projection_type)
    return list(session.execute(stmt).scalars().all())


def assess_projection_conflict(session: Session, asset_id: UUID, projection_type: str) -> OperationResult:
    """REQ-B4-101: generic CPL MUST NOT arbitrarily choose between
    conflicting CURRENT projections of the same type. More than one
    CURRENT projection of the same type for the same Asset is reported
    as requiring domain reconciliation, not silently resolved here."""
    current = current_projections_for_asset(session, asset_id, projection_type)
    if len(current) <= 1:
        return OperationResult(outcome=OperationOutcome.SUCCESS, detail="no conflict")
    return OperationResult(
        outcome=OperationOutcome.CONFLICTING,
        detail="DOMAIN_RECONCILIATION_REQUIRED",
        payload={"conflicting_projection_ids": [p.projection_id for p in current]},
    )
