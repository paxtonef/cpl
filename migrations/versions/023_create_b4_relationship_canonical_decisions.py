"""Create canonical_relationship_decisions and relationship_mutation_requests
(REQ-B4-120..132, REQ-B4-243/244, REQ-B4-252/253/254).

Revision ID: 023
Revises: 022
Create Date: 2026-09-04
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "023"
down_revision: Union[str, Sequence[str], None] = "022"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "canonical_relationship_decisions",
        sa.Column("decision_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "relationship_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cpl.contact_asset_relationships.relationship_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("decision_type", sa.Text(), nullable=False),
        sa.Column("evidence", postgresql.JSONB(), nullable=True),
        sa.Column("authority_context", postgresql.JSONB(), nullable=True),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("result", sa.Text(), nullable=False),
        sa.Column(
            "supersedes_decision_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cpl.canonical_relationship_decisions.decision_id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.CheckConstraint(
            "decision_type IN ('ESTABLISH', 'END', 'CORRECT', 'SUPERSEDE')",
            name="canonical_relationship_decisions_type_chk",
        ),
        sa.CheckConstraint(
            "result IN ('EXECUTED', 'HOLD', 'REJECTED')",
            name="canonical_relationship_decisions_result_chk",
        ),
        schema="cpl",
    )
    op.create_index(
        "ix_canonical_relationship_decisions_relationship",
        "canonical_relationship_decisions",
        ["relationship_id"],
        schema="cpl",
    )

    op.create_table(
        "relationship_mutation_requests",
        sa.Column("idempotency_key", sa.Text(), primary_key=True),
        sa.Column(
            "decision_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cpl.canonical_relationship_decisions.decision_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        schema="cpl",
    )


def downgrade() -> None:
    op.drop_table("relationship_mutation_requests", schema="cpl")
    op.drop_index("ix_canonical_relationship_decisions_relationship", table_name="canonical_relationship_decisions", schema="cpl")
    op.drop_table("canonical_relationship_decisions", schema="cpl")
