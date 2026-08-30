"""Create assets table

Revision ID: 005
Revises: 004
Create Date: 2026-08-28
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "005"
down_revision: Union[str, Sequence[str], None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "assets",
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("asset_domain", sa.Text, nullable=False),
        sa.Column("asset_type", sa.Text, nullable=False),
        sa.Column("asset_status", sa.Text, nullable=False, server_default="UNKNOWN"),
        sa.Column("display_name", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("asset_status IN ('UNKNOWN', 'ACTIVE', 'INACTIVE', 'DISPOSED', 'ARCHIVED')", name="assets_status_chk"),
        schema="cpl",
    )
    op.create_index("assets_domain_idx", "assets", ["asset_domain"], schema="cpl")
    op.create_index("assets_type_idx", "assets", ["asset_type"], schema="cpl")
    op.create_index("assets_status_idx", "assets", ["asset_status"], schema="cpl")
    op.create_index("assets_domain_type_idx", "assets", ["asset_domain", "asset_type"], schema="cpl")


def downgrade() -> None:
    op.drop_index("assets_domain_type_idx", table_name="assets", schema="cpl")
    op.drop_index("assets_status_idx", table_name="assets", schema="cpl")
    op.drop_index("assets_type_idx", table_name="assets", schema="cpl")
    op.drop_index("assets_domain_idx", table_name="assets", schema="cpl")
    op.drop_table("assets", schema="cpl")
