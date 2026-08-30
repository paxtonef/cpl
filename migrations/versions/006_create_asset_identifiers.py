"""Create asset_identifiers table

Revision ID: 006
Revises: 005
Create Date: 2026-08-28
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "006"
down_revision: Union[str, Sequence[str], None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "asset_identifiers",
        sa.Column("asset_identifier_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("identifier_type", sa.Text, nullable=False),
        sa.Column("identifier_value", sa.Text, nullable=False),
        sa.Column("normalized_value", sa.Text, nullable=True),
        sa.Column("country", sa.Text, nullable=True),
        sa.Column("source", sa.Text, nullable=True),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=True),
        sa.Column("identifier_status", sa.Text, nullable=False, server_default="OBSERVED"),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("identifier_status IN ('OBSERVED', 'VERIFIED', 'DISPUTED', 'SUPERSEDED', 'INVALIDATED')", name="asset_identifiers_status_chk"),
        sa.CheckConstraint("confidence IS NULL OR (confidence >= 0 AND confidence <= 1)", name="asset_identifiers_confidence_chk"),
        sa.CheckConstraint("valid_until IS NULL OR valid_from IS NULL OR valid_until >= valid_from", name="asset_identifiers_validity_chk"),
        sa.ForeignKeyConstraint(["asset_id"], ["cpl.assets.asset_id"], ondelete="RESTRICT", name="asset_identifiers_asset_fk"),
        schema="cpl",
    )
    op.create_index("asset_identifiers_lookup_idx", "asset_identifiers", ["identifier_type", "normalized_value"], schema="cpl")
    op.create_index("asset_identifiers_asset_type_idx", "asset_identifiers", ["asset_id", "identifier_type"], schema="cpl")
    op.create_index("asset_identifiers_asset_status_idx", "asset_identifiers", ["asset_id", "identifier_status"], schema="cpl")


def downgrade() -> None:
    op.drop_index("asset_identifiers_asset_status_idx", table_name="asset_identifiers", schema="cpl")
    op.drop_index("asset_identifiers_asset_type_idx", table_name="asset_identifiers", schema="cpl")
    op.drop_index("asset_identifiers_lookup_idx", table_name="asset_identifiers", schema="cpl")
    op.drop_table("asset_identifiers", schema="cpl")
