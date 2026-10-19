"""B2 source-veracity correction: add OWNER_ATTESTED_UNVERIFIED freshness state.

Provenance/authority/freshness truthfulness only -- no diagnostic semantics.

The freshness_status column previously defaulted to VERIFIED_CURRENT and
offered no way to say "supplied/attested by the owner but not
independently verified". Rows that claim VERIFIED_CURRENT while
verified_at IS NULL assert a verification that cannot be demonstrated
(the Peugeot 3008/5008 seed is one such case; the original source PDF
is not currently recoverable). This migration:

  1. widens the CHECK constraint with OWNER_ATTESTED_UNVERIFIED;
  2. changes the column default to OWNER_ATTESTED_UNVERIFIED;
  3. re-labels existing rows with freshness_status = 'VERIFIED_CURRENT'
     AND verified_at IS NULL (an unsupported claim by definition).
     source_authority is deliberately left unchanged (source attribution).

Rows with a real verified_at are untouched. Downgrade restores the
previous constraint/default and maps the new state back to
VERIFIED_CURRENT only because the old schema cannot represent it.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op

revision: str = "029"
down_revision: Union[str, Sequence[str], None] = "028"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLE = "manufacturer_knowledge_documents"
_CHK = "mfr_knowledge_documents_freshness_chk"
_OLD = "freshness_status IN ('VERIFIED_CURRENT', 'STALE', 'SOURCE_UPDATE_REQUIRED', 'SOURCE_UNAVAILABLE')"
_NEW = (
    "freshness_status IN ('VERIFIED_CURRENT', 'STALE', 'SOURCE_UPDATE_REQUIRED', "
    "'SOURCE_UNAVAILABLE', 'OWNER_ATTESTED_UNVERIFIED')"
)


def upgrade() -> None:
    op.drop_constraint(_CHK, _TABLE, schema="cpl", type_="check")
    op.create_check_constraint(_CHK, _TABLE, _NEW, schema="cpl")
    op.alter_column(
        _TABLE, "freshness_status", schema="cpl", server_default="OWNER_ATTESTED_UNVERIFIED",
    )
    op.execute(
        "UPDATE cpl.manufacturer_knowledge_documents "
        "SET freshness_status = 'OWNER_ATTESTED_UNVERIFIED' "
        "WHERE freshness_status = 'VERIFIED_CURRENT' AND verified_at IS NULL"
    )


def downgrade() -> None:
    op.execute(
        "UPDATE cpl.manufacturer_knowledge_documents "
        "SET freshness_status = 'VERIFIED_CURRENT' "
        "WHERE freshness_status = 'OWNER_ATTESTED_UNVERIFIED'"
    )
    op.alter_column(_TABLE, "freshness_status", schema="cpl", server_default="VERIFIED_CURRENT")
    op.drop_constraint(_CHK, _TABLE, schema="cpl", type_="check")
    op.create_check_constraint(_CHK, _TABLE, _OLD, schema="cpl")
