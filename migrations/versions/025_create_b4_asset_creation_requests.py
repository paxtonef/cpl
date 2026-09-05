"""Create asset_creation_requests idempotency ledger (REQ-B4-009..014,
mirrors B3's contact_creation_requests pattern).

Revision ID: 025
Revises: 024
Create Date: 2026-09-04
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "025"
down_revision: Union[str, Sequence[str], None] = "024"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "asset_creation_requests",
        sa.Column("idempotency_key", sa.Text(), primary_key=True),
        sa.Column(
            "asset_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cpl.assets.asset_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        schema="cpl",
    )


def downgrade() -> None:
    op.drop_table("asset_creation_requests", schema="cpl")
