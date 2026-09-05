"""Asset creation admission (REQ-B4-009..014, F02).

NOT_FOUND from a resolution attempt MUST NOT itself create an Asset
(REQ-B4-009) — this module is the only sanctioned creation path, and
it always requires an explicit, separately-governed call with its own
idempotency key (REQ-B4-010/012/013). A domain resolver establishing
"no existing Asset resolved" does not, by itself, invoke this function
or acquire creation authority (REQ-B4-014) — that remains a caller
(CPL admission layer) decision.
"""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.cpl.assets.authority import AssetAuthority, AuthorityContext
from app.cpl.assets.outcomes import OperationOutcome, OperationResult
from app.cpl.models.asset import Asset
from app.cpl.models.asset_creation_request import AssetCreationRequest


def create_asset(
    session: Session, *, asset_domain: str, asset_type: str, display_name: Optional[str] = None,
    authority: AuthorityContext, idempotency_key: str,
) -> OperationResult:
    """REQ-B4-010/011: separate governed creation admission with
    durable provenance (the AssetCreationRequest ledger row itself is
    the minimal provenance: which governed request created which
    Asset). REQ-B4-012/013: idempotent replay by governed request
    identity, never by supplied-evidence similarity — two distinct
    idempotency_keys with identical domain/type/display_name legally
    create two distinct Assets."""
    authority.require(AssetAuthority.CREATE_ASSET)

    existing = session.get(AssetCreationRequest, idempotency_key)
    if existing is not None:
        return OperationResult(outcome=OperationOutcome.SUCCESS, object_id=existing.asset_id, payload={"replay": True})

    asset = Asset(asset_domain=asset_domain, asset_type=asset_type, asset_status="ACTIVE", display_name=display_name)
    session.add(asset)
    session.flush()

    session.add(AssetCreationRequest(idempotency_key=idempotency_key, asset_id=asset.asset_id))
    session.flush()

    return OperationResult(outcome=OperationOutcome.SUCCESS, object_id=asset.asset_id)
