"""Create runner_artifacts table

Revision ID: 012
Revises: 011
Create Date: 2026-08-28
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "012"
down_revision: Union[str, Sequence[str], None] = "011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "runner_artifacts",
        sa.Column("artifact_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("execution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("artifact_type", sa.Text, nullable=False),
        sa.Column("schema_name", sa.Text, nullable=False),
        sa.Column("schema_version", sa.Text, nullable=False),
        sa.Column("artifact_status", sa.Text, nullable=False, server_default="CREATED"),
        sa.Column("payload", postgresql.JSONB, nullable=False),
        sa.Column("hash_algorithm", sa.Text, nullable=True),
        sa.Column("content_hash", sa.Text, nullable=True),
        sa.Column("supersedes_artifact_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("artifact_status IN ('CREATED', 'VALIDATED', 'SUPERSEDED', 'REJECTED')", name="runner_artifacts_status_chk"),
        sa.CheckConstraint("supersedes_artifact_id IS NULL OR supersedes_artifact_id <> artifact_id", name="runner_artifacts_not_self_superseded_chk"),
        sa.CheckConstraint(
            "(hash_algorithm IS NULL AND content_hash IS NULL) OR (hash_algorithm IS NOT NULL AND content_hash IS NOT NULL)",
            name="runner_artifacts_hash_pair_chk",
        ),
        sa.ForeignKeyConstraint(["execution_id"], ["cpl.runner_executions.execution_id"], ondelete="RESTRICT", name="runner_artifacts_execution_fk"),
        sa.ForeignKeyConstraint(["supersedes_artifact_id"], ["cpl.runner_artifacts.artifact_id"], ondelete="RESTRICT", name="runner_artifacts_supersedes_fk"),
        schema="cpl",
    )
    op.create_index("runner_artifacts_execution_idx", "runner_artifacts", ["execution_id"], schema="cpl")
    op.create_index("runner_artifacts_type_idx", "runner_artifacts", ["artifact_type"], schema="cpl")
    op.create_index("runner_artifacts_execution_type_idx", "runner_artifacts", ["execution_id", "artifact_type"], schema="cpl")
    op.create_index("runner_artifacts_supersedes_idx", "runner_artifacts", ["supersedes_artifact_id"], schema="cpl", postgresql_where=sa.text("supersedes_artifact_id IS NOT NULL"))


def downgrade() -> None:
    op.drop_index("runner_artifacts_supersedes_idx", table_name="runner_artifacts", schema="cpl")
    op.drop_index("runner_artifacts_execution_type_idx", table_name="runner_artifacts", schema="cpl")
    op.drop_index("runner_artifacts_type_idx", table_name="runner_artifacts", schema="cpl")
    op.drop_index("runner_artifacts_execution_idx", table_name="runner_artifacts", schema="cpl")
    op.drop_table("runner_artifacts", schema="cpl")
