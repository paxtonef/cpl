"""B6 amendment REQ-B6-091: governed expurgation of vehicle identifiers.

Schema only -- no data is read, changed or removed by this migration:

  1. cpl.runner_artifacts.redaction_status (NULL | 'REDACTED');
  2. cpl.runner_artifact_redactions: one trace row per expurgated artifact
     (operation, reason, opaque operator reference, original and remaining
     content hashes, removed locations by name -- never their values);
  3. runner_governance_decisions_type_chk widened with ARTIFACT_REDACTION.

The expurgation itself is app.cpl.runners.redaction, run by an operator
(simulation by default). Downgrade is refused once any artifact has been
expurgated: its original content no longer exists to be represented.
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "030"
down_revision: Union[str, Sequence[str], None] = "029"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_DECISION_CHK = "runner_governance_decisions_type_chk"
_OLD_TYPES = ("decision_type IN ('EXECUTION_ADMISSION', 'EXECUTION_STATUS_TRANSITION', "
              "'ARTIFACT_REGISTRATION', 'ARTIFACT_SUPERSESSION')")
_NEW_TYPES = ("decision_type IN ('EXECUTION_ADMISSION', 'EXECUTION_STATUS_TRANSITION', "
              "'ARTIFACT_REGISTRATION', 'ARTIFACT_SUPERSESSION', 'ARTIFACT_REDACTION')")


def upgrade() -> None:
    op.add_column("runner_artifacts", sa.Column("redaction_status", sa.Text(), nullable=True), schema="cpl")
    op.create_check_constraint("runner_artifacts_redaction_status_chk", "runner_artifacts",
                               "redaction_status IS NULL OR redaction_status = 'REDACTED'", schema="cpl")
    op.drop_constraint(_DECISION_CHK, "runner_governance_decisions", schema="cpl", type_="check")
    op.create_check_constraint(_DECISION_CHK, "runner_governance_decisions", _NEW_TYPES, schema="cpl")
    op.create_table(
        "runner_artifact_redactions",
        sa.Column("artifact_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("cpl.runner_artifacts.artifact_id", ondelete="RESTRICT"), primary_key=True),
        sa.Column("decision_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("cpl.runner_governance_decisions.decision_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("operation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("operation", sa.Text(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("operator_reference", sa.Text(), nullable=False),
        sa.Column("redacted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("original_hash_algorithm", sa.Text(), nullable=True),
        sa.Column("original_content_hash", sa.Text(), nullable=True),
        sa.Column("hash_algorithm", sa.Text(), nullable=False),
        sa.Column("redacted_content_hash", sa.Text(), nullable=False),
        sa.Column("redacted_locations", postgresql.JSONB(), nullable=False),
        sa.CheckConstraint("operation = 'VEHICLE_IDENTIFIER_REDACTION'", name="runner_artifact_redactions_operation_chk"),
        sa.CheckConstraint("reason IN ('RETENTION_POLICY', 'DATA_SUBJECT_REQUEST')",
                           name="runner_artifact_redactions_reason_chk"),
        sa.CheckConstraint(
            "(original_hash_algorithm IS NULL AND original_content_hash IS NULL) OR "
            "(original_hash_algorithm IS NOT NULL AND original_content_hash IS NOT NULL)",
            name="runner_artifact_redactions_original_hash_pair_chk"),
        schema="cpl",
    )
    op.create_index("ix_runner_artifact_redactions_operation_id", "runner_artifact_redactions", ["operation_id"],
                    schema="cpl")


def downgrade() -> None:
    bind = op.get_bind()
    if bind.execute(sa.text("SELECT 1 FROM cpl.runner_artifact_redactions LIMIT 1")).first() is not None:
        raise RuntimeError("030 downgrade refused: expurgated artifacts exist (their original content is gone)")
    op.drop_index("ix_runner_artifact_redactions_operation_id", "runner_artifact_redactions", schema="cpl")
    op.drop_table("runner_artifact_redactions", schema="cpl")
    op.drop_constraint(_DECISION_CHK, "runner_governance_decisions", schema="cpl", type_="check")
    op.create_check_constraint(_DECISION_CHK, "runner_governance_decisions", _OLD_TYPES, schema="cpl")
    op.drop_constraint("runner_artifacts_redaction_status_chk", "runner_artifacts", schema="cpl", type_="check")
    op.drop_column("runner_artifacts", "redaction_status", schema="cpl")
