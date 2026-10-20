"""B5 amendment REQ-B5-116: governed deletion of an expired Case.

Schema only -- no data is read, changed or removed by this migration:

  cpl.case_deletions: one technical trace row per deleted Case (opaque case
  identifier, operation, reason, retention period, opaque operator
  reference, deleted row counts -- never any content of the Case).

No foreign key is altered and no trigger is created or disabled: the
deletion itself is app.cpl.cases.deletion, which removes the rows in the
order the RESTRICT foreign keys impose. Downgrade is refused once any Case
has been deleted: the deletions are irreversible and their trace is the
only record that they happened.
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "031"
down_revision: Union[str, Sequence[str], None] = "030"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "case_deletions",
        sa.Column("case_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("operation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("retention_days", sa.Integer(), nullable=False),
        sa.Column("anchor", sa.Text(), nullable=False),
        sa.Column("operator_reference", sa.Text(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_counts", postgresql.JSONB(), nullable=False),
        sa.CheckConstraint("reason = 'RETENTION_POLICY'", name="case_deletions_reason_chk"),
        sa.CheckConstraint("anchor = 'creation_dossier'", name="case_deletions_anchor_chk"),
        sa.CheckConstraint("retention_days >= 1", name="case_deletions_retention_days_chk"),
        schema="cpl",
    )
    op.create_index("ix_case_deletions_operation_id", "case_deletions", ["operation_id"], schema="cpl")


def downgrade() -> None:
    bind = op.get_bind()
    if bind.execute(sa.text("SELECT 1 FROM cpl.case_deletions LIMIT 1")).first() is not None:
        raise RuntimeError("031 downgrade refused: Cases have been deleted (irreversible; the trace must stay)")
    op.drop_index("ix_case_deletions_operation_id", "case_deletions", schema="cpl")
    op.drop_table("case_deletions", schema="cpl")
