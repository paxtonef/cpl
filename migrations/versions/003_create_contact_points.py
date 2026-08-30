"""Create contact_points table

Revision ID: 003
Revises: 002
Create Date: 2026-08-28
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, Sequence[str], None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "contact_points",
        sa.Column("contact_point_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("contact_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("point_type", sa.Text, nullable=False),
        sa.Column("raw_value", sa.Text, nullable=False),
        sa.Column("normalized_value", sa.Text, nullable=False),
        sa.Column("verification_status", sa.Text, nullable=False, server_default="UNVERIFIED"),
        sa.Column("is_primary", sa.Boolean, nullable=False, server_default="FALSE"),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("point_type IN ('EMAIL', 'PHONE')", name="contact_points_type_chk"),
        sa.CheckConstraint("verification_status IN ('UNVERIFIED', 'PENDING', 'VERIFIED', 'FAILED', 'REVOKED')", name="contact_points_verification_chk"),
        sa.CheckConstraint("valid_until IS NULL OR valid_until >= valid_from", name="contact_points_validity_chk"),
        sa.ForeignKeyConstraint(["contact_id"], ["cpl.contacts.contact_id"], ondelete="RESTRICT", name="contact_points_contact_fk"),
        schema="cpl",
    )
    op.create_index("contact_points_lookup_idx", "contact_points", ["point_type", "normalized_value"], schema="cpl")
    op.create_index("contact_points_contact_idx", "contact_points", ["contact_id"], schema="cpl")
    op.create_index(
        "contact_points_one_active_primary_idx",
        "contact_points",
        ["contact_id", "point_type"],
        unique=True,
        schema="cpl",
        postgresql_where=sa.text("is_primary = TRUE AND valid_until IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("contact_points_one_active_primary_idx", table_name="contact_points", schema="cpl")
    op.drop_index("contact_points_contact_idx", table_name="contact_points", schema="cpl")
    op.drop_index("contact_points_lookup_idx", table_name="contact_points", schema="cpl")
    op.drop_table("contact_points", schema="cpl")
