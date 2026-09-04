"""B4 Asset authority classes, reusing the generic AuthorityContext
checker from B3 (app.cpl.identity.authority) — B4 does not implement
a new authorization engine (REQ-B4 F21 boundary, mandate Sec. 28)."""
from __future__ import annotations

from app.cpl.identity.authority import AuthorityContext, AuthorityDeniedError  # noqa: F401


class AssetAuthority:
    READ_ASSET = "READ_ASSET"
    CREATE_ASSET = "CREATE_ASSET"
    MANAGE_ASSET_IDENTIFIER = "MANAGE_ASSET_IDENTIFIER"
    CONSUME_IDENTITY_RESOLUTION = "CONSUME_IDENTITY_RESOLUTION"
    ADMIT_ASSET_MERGE = "ADMIT_ASSET_MERGE"
    EXECUTE_ASSET_MERGE = "EXECUTE_ASSET_MERGE"
    CORRECT_ASSET_IDENTITY = "CORRECT_ASSET_IDENTITY"
    MANAGE_RELATIONSHIP = "MANAGE_RELATIONSHIP"
