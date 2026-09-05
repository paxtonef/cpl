"""Create canonical_asset_identity_decisions and asset_merge_requests
(REQ-B4-037..046, REQ-B4-241/242, REQ-B4-250/251/253/254), and add
merged_into_id / MERGED status to assets (REQ-B4-059/060/070..077).

Revision ID: 022
Revises: 021
Create Date: 2026-09-04
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "022"
down_revision: Union[str, Sequence[str], None] = "021"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Asset: survivor/merge pointer (mirrors Contact.merged_into_id) ---
    op.add_column(
        "assets",
        sa.Column("merged_into_id", postgresql.UUID(as_uuid=True), nullable=True),
        schema="cpl",
    )
    op.create_foreign_key(
        "assets_merged_into_id_fkey",
        "assets",
        "assets",
        ["merged_into_id"],
        ["asset_id"],
        source_schema="cpl",
        referent_schema="cpl",
        ondelete="RESTRICT",
    )
    op.drop_constraint("assets_status_chk", "assets", schema="cpl", type_="check")
    op.create_check_constraint(
        "assets_status_chk",
        "assets",
        "asset_status IN ('UNKNOWN', 'ACTIVE', 'INACTIVE', 'DISPOSED', 'ARCHIVED', 'MERGED')",
        schema="cpl",
    )
    op.create_check_constraint(
        "assets_not_self_merged_chk",
        "assets",
        "merged_into_id IS NULL OR merged_into_id <> asset_id",
        schema="cpl",
    )
    op.create_check_constraint(
        "assets_merged_target_required_chk",
        "assets",
        "asset_status <> 'MERGED' OR merged_into_id IS NOT NULL",
        schema="cpl",
    )

    # --- CanonicalAssetIdentityDecision (REQ-B4-037..046) ---
    op.create_table(
        "canonical_asset_identity_decisions",
        sa.Column("decision_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("decision_type", sa.Text(), nullable=False),
        sa.Column(
            "source_asset_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cpl.assets.asset_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "target_asset_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cpl.assets.asset_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "resolution_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cpl.asset_identity_resolutions.resolution_id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column("survivor_rule_applied", sa.Text(), nullable=True),
        sa.Column("survivor_override_reason", sa.Text(), nullable=True),
        sa.Column("dependency_disposition", postgresql.JSONB(), nullable=True),
        sa.Column("authority_context", postgresql.JSONB(), nullable=True),
        sa.Column("result", sa.Text(), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "supersedes_decision_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cpl.canonical_asset_identity_decisions.decision_id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.CheckConstraint(
            "decision_type IN ('MERGE', 'CORRECTION')",
            name="canonical_asset_identity_decisions_type_chk",
        ),
        sa.CheckConstraint(
            "result IN ('EXECUTED', 'HOLD', 'REJECTED')",
            name="canonical_asset_identity_decisions_result_chk",
        ),
        sa.CheckConstraint(
            "source_asset_id <> target_asset_id",
            name="canonical_asset_identity_decisions_not_self_chk",
        ),
        schema="cpl",
    )
    op.create_index(
        "ix_canonical_asset_identity_decisions_source",
        "canonical_asset_identity_decisions",
        ["source_asset_id"],
        schema="cpl",
    )
    op.create_index(
        "ix_canonical_asset_identity_decisions_target",
        "canonical_asset_identity_decisions",
        ["target_asset_id"],
        schema="cpl",
    )

    # --- Idempotency ledger for merge/correction requests (REQ-B4-250/251/253/254) ---
    op.create_table(
        "asset_merge_requests",
        sa.Column("idempotency_key", sa.Text(), primary_key=True),
        sa.Column(
            "decision_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cpl.canonical_asset_identity_decisions.decision_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        schema="cpl",
    )


def downgrade() -> None:
    op.drop_table("asset_merge_requests", schema="cpl")
    op.drop_index("ix_canonical_asset_identity_decisions_target", table_name="canonical_asset_identity_decisions", schema="cpl")
    op.drop_index("ix_canonical_asset_identity_decisions_source", table_name="canonical_asset_identity_decisions", schema="cpl")
    op.drop_table("canonical_asset_identity_decisions", schema="cpl")
    op.drop_constraint("assets_merged_target_required_chk", "assets", schema="cpl", type_="check")
    op.drop_constraint("assets_not_self_merged_chk", "assets", schema="cpl", type_="check")
    op.drop_constraint("assets_status_chk", "assets", schema="cpl", type_="check")
    op.create_check_constraint(
        "assets_status_chk",
        "assets",
        "asset_status IN ('UNKNOWN', 'ACTIVE', 'INACTIVE', 'DISPOSED', 'ARCHIVED')",
        schema="cpl",
    )
    op.drop_constraint("assets_merged_into_id_fkey", "assets", schema="cpl", type_="foreignkey")
    op.drop_column("assets", "merged_into_id", schema="cpl")
