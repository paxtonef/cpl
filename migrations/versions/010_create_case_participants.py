"""Create case_participants table

Revision ID: 010
Revises: 009
Create Date: 2026-08-28
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "010"
down_revision: Union[str, Sequence[str], None] = "009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "case_participants",
        sa.Column("case_participant_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contact_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("participant_role", sa.Text, nullable=False),
        sa.Column("participant_status", sa.Text, nullable=False, server_default="ACTIVE"),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("left_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("participant_status IN ('ACTIVE', 'LEFT', 'REMOVED')", name="case_participants_status_chk"),
        sa.CheckConstraint("left_at IS NULL OR left_at >= joined_at", name="case_participants_time_chk"),
        sa.ForeignKeyConstraint(["case_id"], ["cpl.cases.case_id"], ondelete="RESTRICT", name="case_participants_case_fk"),
        sa.ForeignKeyConstraint(["contact_id"], ["cpl.contacts.contact_id"], ondelete="RESTRICT", name="case_participants_contact_fk"),
        schema="cpl",
    )
    op.create_index("case_participants_case_idx", "case_participants", ["case_id"], schema="cpl")
    op.create_index("case_participants_contact_idx", "case_participants", ["contact_id"], schema="cpl")
    op.create_index("case_participants_case_status_idx", "case_participants", ["case_id", "participant_status"], schema="cpl")
    op.create_index(
        "case_participants_active_role_uq",
        "case_participants",
        ["case_id", "contact_id", "participant_role"],
        unique=True,
        schema="cpl",
        postgresql_where=sa.text("participant_status = 'ACTIVE'"),
    )


def downgrade() -> None:
    op.drop_index("case_participants_active_role_uq", table_name="case_participants", schema="cpl")
    op.drop_index("case_participants_case_status_idx", table_name="case_participants", schema="cpl")
    op.drop_index("case_participants_contact_idx", table_name="case_participants", schema="cpl")
    op.drop_index("case_participants_case_idx", table_name="case_participants", schema="cpl")
    op.drop_table("case_participants", schema="cpl")
