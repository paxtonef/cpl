"""Create case_events table

Revision ID: 013
Revises: 012
Create Date: 2026-08-28
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "013"
down_revision: Union[str, Sequence[str], None] = "012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "case_events",
        sa.Column("event_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.Text, nullable=False),
        sa.Column("actor_type", sa.Text, nullable=False),
        sa.Column("actor_reference_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("execution_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("payload", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("actor_type IN ('CONTACT', 'SYSTEM', 'RUNNER', 'ADMIN', 'EXTERNAL_PARTY')", name="case_events_actor_type_chk"),
        sa.ForeignKeyConstraint(["case_id"], ["cpl.cases.case_id"], ondelete="RESTRICT", name="case_events_case_fk"),
        sa.ForeignKeyConstraint(["execution_id"], ["cpl.runner_executions.execution_id"], ondelete="RESTRICT", name="case_events_execution_fk"),
        schema="cpl",
    )
    op.create_index("case_events_case_idx", "case_events", ["case_id"], schema="cpl")
    op.create_index("case_events_case_occurred_idx", "case_events", ["case_id", "occurred_at"], schema="cpl")
    op.create_index("case_events_type_idx", "case_events", ["event_type"], schema="cpl")
    op.create_index("case_events_execution_idx", "case_events", ["execution_id"], schema="cpl", postgresql_where=sa.text("execution_id IS NOT NULL"))


def downgrade() -> None:
    op.drop_index("case_events_execution_idx", table_name="case_events", schema="cpl")
    op.drop_index("case_events_type_idx", table_name="case_events", schema="cpl")
    op.drop_index("case_events_case_occurred_idx", table_name="case_events", schema="cpl")
    op.drop_index("case_events_case_idx", table_name="case_events", schema="cpl")
    op.drop_table("case_events", schema="cpl")
