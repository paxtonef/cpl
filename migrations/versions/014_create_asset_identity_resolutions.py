"""Create asset_identity_resolutions table

Revision ID: 014
Revises: 013
Create Date: 2026-08-28
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "014"
down_revision: Union[str, Sequence[str], None] = "013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "asset_identity_resolutions",
        sa.Column("resolution_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("resolver_type", sa.Text, nullable=False),
        sa.Column("resolver_version", sa.Text, nullable=False),
        sa.Column("execution_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("resolution_status", sa.Text, nullable=False),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=True),
        sa.Column("canonical_identity_payload", postgresql.JSONB, nullable=False),
        sa.Column("provenance_payload", postgresql.JSONB, nullable=True),
        sa.Column("supersedes_resolution_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("resolution_status IN ('RESOLVED', 'PARTIALLY_RESOLVED', 'AMBIGUOUS', 'CONTRADICTORY', 'UNRESOLVED', 'FAILED')", name="asset_identity_resolutions_status_chk"),
        sa.CheckConstraint("confidence IS NULL OR (confidence >= 0 AND confidence <= 1)", name="asset_identity_resolutions_confidence_chk"),
        sa.CheckConstraint("supersedes_resolution_id IS NULL OR supersedes_resolution_id <> resolution_id", name="asset_identity_resolutions_not_self_superseded_chk"),
        sa.ForeignKeyConstraint(["asset_id"], ["cpl.assets.asset_id"], ondelete="RESTRICT", name="asset_identity_resolutions_asset_fk"),
        sa.ForeignKeyConstraint(["execution_id"], ["cpl.runner_executions.execution_id"], ondelete="RESTRICT", name="asset_identity_resolutions_execution_fk"),
        sa.ForeignKeyConstraint(["supersedes_resolution_id"], ["cpl.asset_identity_resolutions.resolution_id"], ondelete="RESTRICT", name="asset_identity_resolutions_supersedes_fk"),
        schema="cpl",
    )
    op.create_index("asset_identity_resolutions_asset_idx", "asset_identity_resolutions", ["asset_id"], schema="cpl")
    op.create_index("asset_identity_resolutions_asset_created_idx", "asset_identity_resolutions", ["asset_id", sa.text("created_at DESC")], schema="cpl")
    op.create_index("asset_identity_resolutions_resolver_idx", "asset_identity_resolutions", ["resolver_type", "resolver_version"], schema="cpl")
    op.create_index("asset_identity_resolutions_execution_idx", "asset_identity_resolutions", ["execution_id"], schema="cpl", postgresql_where=sa.text("execution_id IS NOT NULL"))
    op.create_index("asset_identity_resolutions_supersedes_idx", "asset_identity_resolutions", ["supersedes_resolution_id"], schema="cpl", postgresql_where=sa.text("supersedes_resolution_id IS NOT NULL"))


def downgrade() -> None:
    op.drop_index("asset_identity_resolutions_supersedes_idx", table_name="asset_identity_resolutions", schema="cpl")
    op.drop_index("asset_identity_resolutions_execution_idx", table_name="asset_identity_resolutions", schema="cpl")
    op.drop_index("asset_identity_resolutions_resolver_idx", table_name="asset_identity_resolutions", schema="cpl")
    op.drop_index("asset_identity_resolutions_asset_created_idx", table_name="asset_identity_resolutions", schema="cpl")
    op.drop_index("asset_identity_resolutions_asset_idx", table_name="asset_identity_resolutions", schema="cpl")
    op.drop_table("asset_identity_resolutions", schema="cpl")
