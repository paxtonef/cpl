"""Create runner_executions table

Revision ID: 011
Revises: 010
Create Date: 2026-08-28
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "011"
down_revision: Union[str, Sequence[str], None] = "010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "runner_executions",
        sa.Column("execution_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("runner_type", sa.Text, nullable=False),
        sa.Column("runner_version", sa.Text, nullable=False),
        sa.Column("execution_purpose", sa.Text, nullable=True),
        sa.Column("execution_status", sa.Text, nullable=False, server_default="CREATED"),
        sa.Column("parent_execution_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("initiated_by_contact_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("idempotency_key", sa.Text, nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("execution_status IN ('CREATED', 'QUEUED', 'RUNNING', 'COMPLETED', 'FAILED', 'BLOCKED', 'CANCELLED')", name="runner_executions_status_chk"),
        sa.CheckConstraint("parent_execution_id IS NULL OR parent_execution_id <> execution_id", name="runner_executions_not_self_parent_chk"),
        sa.CheckConstraint("completed_at IS NULL OR started_at IS NULL OR completed_at >= started_at", name="runner_executions_time_chk"),
        sa.CheckConstraint("execution_status <> 'COMPLETED' OR completed_at IS NOT NULL", name="runner_executions_completed_at_chk"),
        sa.ForeignKeyConstraint(["case_id"], ["cpl.cases.case_id"], ondelete="RESTRICT", name="runner_executions_case_fk"),
        sa.ForeignKeyConstraint(["asset_id"], ["cpl.assets.asset_id"], ondelete="RESTRICT", name="runner_executions_asset_fk"),
        sa.ForeignKeyConstraint(["parent_execution_id"], ["cpl.runner_executions.execution_id"], ondelete="RESTRICT", name="runner_executions_parent_fk"),
        sa.ForeignKeyConstraint(["initiated_by_contact_id"], ["cpl.contacts.contact_id"], ondelete="RESTRICT", name="runner_executions_initiator_fk"),
        schema="cpl",
    )
    op.create_index("runner_executions_case_idx", "runner_executions", ["case_id"], schema="cpl")
    op.create_index("runner_executions_asset_idx", "runner_executions", ["asset_id"], schema="cpl")
    op.create_index("runner_executions_runner_type_idx", "runner_executions", ["runner_type"], schema="cpl")
    op.create_index("runner_executions_status_idx", "runner_executions", ["execution_status"], schema="cpl")
    op.create_index("runner_executions_case_started_idx", "runner_executions", ["case_id", sa.text("started_at DESC")], schema="cpl")
    op.create_index("runner_executions_parent_idx", "runner_executions", ["parent_execution_id"], schema="cpl", postgresql_where=sa.text("parent_execution_id IS NOT NULL"))
    op.create_index(
        "runner_executions_idempotency_uq",
        "runner_executions",
        ["runner_type", "idempotency_key"],
        unique=True,
        schema="cpl",
        postgresql_where=sa.text("idempotency_key IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("runner_executions_idempotency_uq", table_name="runner_executions", schema="cpl")
    op.drop_index("runner_executions_parent_idx", table_name="runner_executions", schema="cpl")
    op.drop_index("runner_executions_case_started_idx", table_name="runner_executions", schema="cpl")
    op.drop_index("runner_executions_status_idx", table_name="runner_executions", schema="cpl")
    op.drop_index("runner_executions_runner_type_idx", table_name="runner_executions", schema="cpl")
    op.drop_index("runner_executions_asset_idx", table_name="runner_executions", schema="cpl")
    op.drop_index("runner_executions_case_idx", table_name="runner_executions", schema="cpl")
    op.drop_table("runner_executions", schema="cpl")
