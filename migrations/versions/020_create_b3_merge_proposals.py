"""Create merge_proposals — durable PROPOSE_MERGE artifact (REQ-B3-042/043/044, RM-O01)

Revision ID: 020
Revises: 019
Create Date: 2026-09-02
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "020"
down_revision: Union[str, Sequence[str], None] = "019"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "merge_proposals",
        sa.Column("proposal_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("source_contact_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("target_contact_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("evidence", postgresql.JSONB, nullable=True),
        sa.Column("proposed_by", sa.Text, nullable=True),
        sa.Column("status", sa.Text, nullable=False, server_default="PROPOSED"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("status IN ('PROPOSED', 'AUTHORIZED', 'EXECUTED', 'REJECTED')", name="merge_proposals_status_chk"),
        sa.CheckConstraint("source_contact_id <> target_contact_id", name="merge_proposals_not_self_chk"),
        sa.ForeignKeyConstraint(["source_contact_id"], ["cpl.contacts.contact_id"], ondelete="RESTRICT", name="merge_proposals_source_fk"),
        sa.ForeignKeyConstraint(["target_contact_id"], ["cpl.contacts.contact_id"], ondelete="RESTRICT", name="merge_proposals_target_fk"),
        schema="cpl",
    )
    op.create_index("merge_proposals_source_idx", "merge_proposals", ["source_contact_id"], schema="cpl")
    op.create_index("merge_proposals_target_idx", "merge_proposals", ["target_contact_id"], schema="cpl")
    op.create_index("merge_proposals_status_idx", "merge_proposals", ["status"], schema="cpl")


def downgrade() -> None:
    op.drop_index("merge_proposals_status_idx", table_name="merge_proposals", schema="cpl")
    op.drop_index("merge_proposals_target_idx", table_name="merge_proposals", schema="cpl")
    op.drop_index("merge_proposals_source_idx", table_name="merge_proposals", schema="cpl")
    op.drop_table("merge_proposals", schema="cpl")
