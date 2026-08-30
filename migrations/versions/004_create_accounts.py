"""Create accounts table

Revision ID: 004
Revises: 003
Create Date: 2026-08-28
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "004"
down_revision: Union[str, Sequence[str], None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("account_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("contact_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("auth_provider", sa.Text, nullable=False),
        sa.Column("provider_subject_id", sa.Text, nullable=False),
        sa.Column("account_status", sa.Text, nullable=False, server_default="PENDING"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("last_authenticated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("disabled_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("account_status IN ('PENDING', 'ACTIVE', 'DISABLED', 'REVOKED')", name="accounts_status_chk"),
        sa.ForeignKeyConstraint(["contact_id"], ["cpl.contacts.contact_id"], ondelete="RESTRICT", name="accounts_contact_fk"),
        sa.UniqueConstraint("auth_provider", "provider_subject_id", name="accounts_provider_identity_uq"),
        schema="cpl",
    )
    op.create_index("accounts_contact_idx", "accounts", ["contact_id"], schema="cpl")
    op.create_index("accounts_status_idx", "accounts", ["account_status"], schema="cpl")


def downgrade() -> None:
    op.drop_index("accounts_status_idx", table_name="accounts", schema="cpl")
    op.drop_index("accounts_contact_idx", table_name="accounts", schema="cpl")
    op.drop_table("accounts", schema="cpl")
