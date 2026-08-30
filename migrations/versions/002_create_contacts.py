"""Create contacts table

Revision ID: 002
Revises: 001
Create Date: 2026-08-28
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "002"
down_revision: Union[str, Sequence[str], None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "contacts",
        sa.Column("contact_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("contact_type", sa.Text, nullable=False),
        sa.Column("display_name", sa.Text, nullable=True),
        sa.Column("first_name", sa.Text, nullable=True),
        sa.Column("last_name", sa.Text, nullable=True),
        sa.Column("contact_status", sa.Text, nullable=False, server_default="ACTIVE"),
        sa.Column("merged_into_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("contact_type IN ('PERSON', 'ORGANIZATION')", name="contacts_type_chk"),
        sa.CheckConstraint("contact_status IN ('ACTIVE', 'MERGED', 'BLOCKED', 'ARCHIVED')", name="contacts_status_chk"),
        sa.CheckConstraint("merged_into_id IS NULL OR merged_into_id <> contact_id", name="contacts_not_self_merged_chk"),
        sa.CheckConstraint("contact_status <> 'MERGED' OR merged_into_id IS NOT NULL", name="contacts_merged_target_required_chk"),
        sa.ForeignKeyConstraint(["merged_into_id"], ["cpl.contacts.contact_id"], ondelete="RESTRICT", name="contacts_merged_into_fk"),
        schema="cpl",
    )
    op.create_index("contacts_status_idx", "contacts", ["contact_status"], schema="cpl")
    op.create_index("contacts_type_idx", "contacts", ["contact_type"], schema="cpl")
    op.create_index("contacts_merged_into_idx", "contacts", ["merged_into_id"], schema="cpl", postgresql_where=sa.text("merged_into_id IS NOT NULL"))


def downgrade() -> None:
    op.drop_index("contacts_merged_into_idx", table_name="contacts", schema="cpl")
    op.drop_index("contacts_type_idx", table_name="contacts", schema="cpl")
    op.drop_index("contacts_status_idx", table_name="contacts", schema="cpl")
    op.drop_table("contacts", schema="cpl")
