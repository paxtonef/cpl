"""Create contact_asset_relationships table

Revision ID: 007
Revises: 006
Create Date: 2026-08-28
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "007"
down_revision: Union[str, Sequence[str], None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "contact_asset_relationships",
        sa.Column("relationship_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("contact_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("relationship_type", sa.Text, nullable=False),
        sa.Column("relationship_status", sa.Text, nullable=False, server_default="UNVERIFIED"),
        sa.Column("source", sa.Text, nullable=True),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("relationship_status IN ('UNVERIFIED', 'ACTIVE', 'DISPUTED', 'ENDED')", name="contact_asset_relationships_status_chk"),
        sa.CheckConstraint("valid_until IS NULL OR valid_from IS NULL OR valid_until >= valid_from", name="contact_asset_relationships_validity_chk"),
        sa.ForeignKeyConstraint(["contact_id"], ["cpl.contacts.contact_id"], ondelete="RESTRICT", name="contact_asset_relationships_contact_fk"),
        sa.ForeignKeyConstraint(["asset_id"], ["cpl.assets.asset_id"], ondelete="RESTRICT", name="contact_asset_relationships_asset_fk"),
        schema="cpl",
    )
    op.create_index("contact_asset_relationships_contact_idx", "contact_asset_relationships", ["contact_id"], schema="cpl")
    op.create_index("contact_asset_relationships_asset_idx", "contact_asset_relationships", ["asset_id"], schema="cpl")
    op.create_index("contact_asset_relationships_contact_status_idx", "contact_asset_relationships", ["contact_id", "relationship_status"], schema="cpl")
    op.create_index("contact_asset_relationships_asset_status_idx", "contact_asset_relationships", ["asset_id", "relationship_status"], schema="cpl")
    op.create_index(
        "contact_asset_relationships_active_uq",
        "contact_asset_relationships",
        ["contact_id", "asset_id", "relationship_type"],
        unique=True,
        schema="cpl",
        postgresql_where=sa.text("relationship_status = 'ACTIVE' AND valid_until IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("contact_asset_relationships_active_uq", table_name="contact_asset_relationships", schema="cpl")
    op.drop_index("contact_asset_relationships_asset_status_idx", table_name="contact_asset_relationships", schema="cpl")
    op.drop_index("contact_asset_relationships_contact_status_idx", table_name="contact_asset_relationships", schema="cpl")
    op.drop_index("contact_asset_relationships_asset_idx", table_name="contact_asset_relationships", schema="cpl")
    op.drop_index("contact_asset_relationships_contact_idx", table_name="contact_asset_relationships", schema="cpl")
    op.drop_table("contact_asset_relationships", schema="cpl")
