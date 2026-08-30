"""Create cases table

Revision ID: 009
Revises: 008
Create Date: 2026-08-28
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "009"
down_revision: Union[str, Sequence[str], None] = "008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cases",
        sa.Column("case_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("primary_contact_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("domain", sa.Text, nullable=False),
        sa.Column("case_type", sa.Text, nullable=False),
        sa.Column("case_status", sa.Text, nullable=False, server_default="OPEN"),
        sa.Column("title", sa.Text, nullable=True),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("case_status IN ('OPEN', 'IN_PROGRESS', 'WAITING_FOR_USER', 'WAITING_FOR_EXTERNAL_INFORMATION', 'RESOLVED', 'CLOSED', 'REOPENED', 'CANCELLED')", name="cases_status_chk"),
        sa.CheckConstraint("case_status <> 'CLOSED' OR closed_at IS NOT NULL", name="cases_closed_at_chk"),
        sa.ForeignKeyConstraint(["primary_contact_id"], ["cpl.contacts.contact_id"], ondelete="RESTRICT", name="cases_primary_contact_fk"),
        sa.ForeignKeyConstraint(["asset_id"], ["cpl.assets.asset_id"], ondelete="RESTRICT", name="cases_asset_fk"),
        schema="cpl",
    )
    op.create_index("cases_primary_contact_idx", "cases", ["primary_contact_id"], schema="cpl")
    op.create_index("cases_asset_idx", "cases", ["asset_id"], schema="cpl")
    op.create_index("cases_status_idx", "cases", ["case_status"], schema="cpl")
    op.create_index("cases_asset_status_idx", "cases", ["asset_id", "case_status"], schema="cpl")
    op.create_index("cases_contact_status_idx", "cases", ["primary_contact_id", "case_status"], schema="cpl")
    op.create_index("cases_opened_at_idx", "cases", [sa.text("opened_at DESC")], schema="cpl")


def downgrade() -> None:
    op.drop_index("cases_opened_at_idx", table_name="cases", schema="cpl")
    op.drop_index("cases_contact_status_idx", table_name="cases", schema="cpl")
    op.drop_index("cases_asset_status_idx", table_name="cases", schema="cpl")
    op.drop_index("cases_status_idx", table_name="cases", schema="cpl")
    op.drop_index("cases_asset_idx", table_name="cases", schema="cpl")
    op.drop_index("cases_primary_contact_idx", table_name="cases", schema="cpl")
    op.drop_table("cases", schema="cpl")
