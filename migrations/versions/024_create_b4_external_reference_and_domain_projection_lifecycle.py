"""Add ExternalReference lifecycle (REQ-B4-087..095), generic
DomainProjection lifecycle table (REQ-B4-096..103), and a self-FK
on canonical_relationship_decisions is already present — this
migration only adds the missing lifecycle surfaces.

Revision ID: 024
Revises: 023
Create Date: 2026-09-04
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "024"
down_revision: Union[str, Sequence[str], None] = "023"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- ExternalReference lifecycle (REQ-B4-093/095) ---
    op.add_column(
        "external_references",
        sa.Column("reference_status", sa.Text(), nullable=False, server_default="CURRENT"),
        schema="cpl",
    )
    op.add_column(
        "external_references",
        sa.Column("superseded_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        schema="cpl",
    )
    op.create_foreign_key(
        "external_references_superseded_by_id_fkey",
        "external_references",
        "external_references",
        ["superseded_by_id"],
        ["external_reference_id"],
        source_schema="cpl",
        referent_schema="cpl",
        ondelete="RESTRICT",
    )
    op.create_check_constraint(
        "external_references_status_chk",
        "external_references",
        "reference_status IN ('CURRENT', 'SUPERSEDED', 'INVALIDATED')",
        schema="cpl",
    )

    # --- Generic DomainProjection lifecycle (REQ-B4-096..103) ---
    # Deliberately decoupled from automotive.vehicle_details: this table
    # governs projection *lifecycle continuity*, not domain-specific
    # payload shape (B4 does not implement VIR/PGDR domain logic).
    op.create_table(
        "domain_projections",
        sa.Column("projection_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "asset_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cpl.assets.asset_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("projection_type", sa.Text(), nullable=False),
        sa.Column("projection_status", sa.Text(), nullable=False, server_default="CURRENT"),
        sa.Column("payload", postgresql.JSONB(), nullable=True),
        sa.Column("domain_authority", sa.Text(), nullable=True),
        sa.Column(
            "source_resolution_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cpl.asset_identity_resolutions.resolution_id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column(
            "supersedes_projection_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cpl.domain_projections.projection_id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "projection_status IN ('ATTACHED', 'CURRENT', 'SUPERSEDED', 'HISTORICAL', 'DISPUTED')",
            name="domain_projections_status_chk",
        ),
        schema="cpl",
    )
    op.create_index("ix_domain_projections_asset", "domain_projections", ["asset_id"], schema="cpl")


def downgrade() -> None:
    op.drop_index("ix_domain_projections_asset", table_name="domain_projections", schema="cpl")
    op.drop_table("domain_projections", schema="cpl")
    op.drop_constraint("external_references_status_chk", "external_references", schema="cpl", type_="check")
    op.drop_constraint("external_references_superseded_by_id_fkey", "external_references", schema="cpl", type_="foreignkey")
    op.drop_column("external_references", "superseded_by_id", schema="cpl")
    op.drop_column("external_references", "reference_status", schema="cpl")
