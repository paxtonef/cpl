"""Governed AssetIdentityResolution operation family
(REQ-B4-182..192, FR-B4-02 / B4-CI32).

Frozen boundary (B4_WHAT_CONSOLIDATION_v0.1 Sec. 50, B4-CI32):
    DOMAIN produces the physical-identity determination.
    CPL requests, consumes, records, and governs admissibility of
    that determination — it never produces one itself.

`request_asset_identity_resolution` therefore does NOT determine
physical identity, does not call any domain resolver implementation
(VIR is explicitly out of B4 scope, Mandate Sec. 8), and does not
fabricate a result. It records that CPL requested a domain
determination for given Asset(s)/evidence; the actual determination
must arrive separately (e.g. via an adapter outside B4) and be
persisted through `record_asset_identity_resolution`.
"""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.cpl.assets.authority import AssetAuthority, AuthorityContext
from app.cpl.assets.outcomes import OperationOutcome, OperationResult
from app.cpl.models.asset import Asset
from app.cpl.models.asset_identity_resolution import AssetIdentityResolution

VALID_RESOLUTION_STATUSES = frozenset({
    "RESOLVED", "PARTIALLY_RESOLVED", "AMBIGUOUS", "CONTRADICTORY", "UNRESOLVED", "FAILED",
})


def request_asset_identity_resolution(
    session: Session, *, asset_ids: list[UUID], resolver_type: str, authority: AuthorityContext,
) -> OperationResult:
    """REQ-B4-182: CPL MAY request domain physical-identity resolution.
    This function performs NO determination itself (B4-CI32) — it only
    validates the Assets exist and returns an acknowledgement payload
    a caller can hand to whatever external domain-resolver integration
    exists outside B4's authorized scope."""
    authority.require(AssetAuthority.CONSUME_IDENTITY_RESOLUTION)

    missing = [aid for aid in asset_ids if session.get(Asset, aid) is None]
    if missing:
        return OperationResult(outcome=OperationOutcome.NOT_FOUND, detail=f"unknown asset_ids: {missing}")

    return OperationResult(
        outcome=OperationOutcome.SUCCESS,
        detail="resolution request acknowledged; determination must be supplied by domain authority",
        payload={"asset_ids": asset_ids, "resolver_type": resolver_type},
    )


def record_asset_identity_resolution(
    session: Session, *, asset_id: UUID, resolver_type: str, resolver_version: str,
    resolution_status: str, canonical_identity_payload: dict, confidence: Optional[float] = None,
    execution_id: Optional[UUID] = None, provenance_payload: Optional[dict] = None,
    supersedes_resolution_id: Optional[UUID] = None, authority: AuthorityContext,
) -> OperationResult:
    """REQ-B4-183/184: CPL MAY consume and persist a domain-produced
    resolution. This function only records what the domain authority
    already determined — it never derives resolution_status itself
    from similarity or any other generic heuristic (REQ-B4-035)."""
    authority.require(AssetAuthority.CONSUME_IDENTITY_RESOLUTION)

    if resolution_status not in VALID_RESOLUTION_STATUSES:
        return OperationResult(outcome=OperationOutcome.INVALID, detail=f"unrecognized resolution_status {resolution_status!r}")

    asset = session.get(Asset, asset_id)
    if asset is None:
        return OperationResult(outcome=OperationOutcome.NOT_FOUND)

    resolution = AssetIdentityResolution(
        asset_id=asset_id, resolver_type=resolver_type, resolver_version=resolver_version,
        execution_id=execution_id, resolution_status=resolution_status, confidence=confidence,
        canonical_identity_payload=canonical_identity_payload, provenance_payload=provenance_payload,
        supersedes_resolution_id=supersedes_resolution_id,
    )
    session.add(resolution)
    session.flush()
    return OperationResult(outcome=OperationOutcome.SUCCESS, object_id=resolution.resolution_id)


def evaluate_asset_resolution_admissibility(session: Session, *, resolution_id: UUID, authority: AuthorityContext) -> OperationResult:
    """REQ-B4-185: CPL MAY evaluate whether a recorded domain
    determination is admissible for canonical action. This is a
    governance/provenance check, never a re-determination of physical
    truth (B4-CI32) — it never overrides resolution_status."""
    authority.require(AssetAuthority.CONSUME_IDENTITY_RESOLUTION)

    resolution = session.get(AssetIdentityResolution, resolution_id)
    if resolution is None:
        return OperationResult(outcome=OperationOutcome.NOT_FOUND)

    reasons = []
    if resolution.resolver_type is None or not resolution.resolver_type.strip():
        reasons.append("missing resolver_type provenance")
    if resolution.resolution_status not in VALID_RESOLUTION_STATUSES:
        reasons.append("unrecognized resolution_status")
    # REQ-B4-034: a superseded resolution is historical, not admissible
    # for a *new* canonical action (though it remains reconstructable).
    superseding = (
        session.query(AssetIdentityResolution)
        .filter(AssetIdentityResolution.supersedes_resolution_id == resolution_id)
        .first()
    )
    if superseding is not None:
        reasons.append(f"superseded by resolution {superseding.resolution_id}")

    if reasons:
        return OperationResult(outcome=OperationOutcome.INVALID, detail="; ".join(reasons), object_id=resolution_id)
    return OperationResult(outcome=OperationOutcome.SUCCESS, object_id=resolution_id,
                            payload={"resolution_status": resolution.resolution_status})
