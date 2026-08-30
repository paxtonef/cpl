"""Add current-state pointer columns and FKs

Revision ID: 016
Revises: 015
Create Date: 2026-08-28
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "016"
down_revision: Union[str, Sequence[str], None] = "015"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # assets: add current_identity_resolution_id column + FK + index
    op.add_column("assets", sa.Column("current_identity_resolution_id", postgresql.UUID(as_uuid=True), nullable=True), schema="cpl")
    op.create_foreign_key(
        "assets_current_resolution_fk",
        "assets",
        "asset_identity_resolutions",
        ["current_identity_resolution_id"],
        ["resolution_id"],
        source_schema="cpl",
        referent_schema="cpl",
        ondelete="RESTRICT",
    )
    op.create_index("assets_current_resolution_idx", "assets", ["current_identity_resolution_id"], schema="cpl", postgresql_where=sa.text("current_identity_resolution_id IS NOT NULL"))

    # cases: add current_execution_id column + FK + index
    op.add_column("cases", sa.Column("current_execution_id", postgresql.UUID(as_uuid=True), nullable=True), schema="cpl")
    op.create_foreign_key(
        "cases_current_execution_fk",
        "cases",
        "runner_executions",
        ["current_execution_id"],
        ["execution_id"],
        source_schema="cpl",
        referent_schema="cpl",
        ondelete="RESTRICT",
    )
    op.create_index("cases_current_execution_idx", "cases", ["current_execution_id"], schema="cpl", postgresql_where=sa.text("current_execution_id IS NOT NULL"))

    # vehicle_details: FK only — source_resolution_id already created in migration 008
    op.create_foreign_key(
        "vehicle_details_source_resolution_fk",
        "vehicle_details",
        "asset_identity_resolutions",
        ["source_resolution_id"],
        ["resolution_id"],
        source_schema="automotive",
        referent_schema="cpl",
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    # vehicle_details: drop FK only — column belongs to migration 008
    op.drop_constraint("vehicle_details_source_resolution_fk", "vehicle_details", schema="automotive", type_="foreignkey")

    op.drop_index("cases_current_execution_idx", table_name="cases", schema="cpl")
    op.drop_constraint("cases_current_execution_fk", "cases", schema="cpl", type_="foreignkey")
    op.drop_column("cases", "current_execution_id", schema="cpl")

    op.drop_index("assets_current_resolution_idx", table_name="assets", schema="cpl")
    op.drop_constraint("assets_current_resolution_fk", "assets", schema="cpl", type_="foreignkey")
    op.drop_column("assets", "current_identity_resolution_id", schema="cpl")
