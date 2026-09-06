"""Create B5 Case Governance canonical decision infrastructure
(REQ-B5-046..051 authority/decision pipeline), case_mutation_requests
idempotency ledger (REQ-B5-075..079, 113), case_event_types semantic
classification registry (REQ-B5-035..038, 115), and CaseEvent
correction/supersession support (REQ-B5-069..074).

Revision ID: 026
Revises: 025
Create Date: 2026-09-07
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "026"
down_revision: Union[str, Sequence[str], None] = "025"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- CanonicalCaseDecision (REQ-B5-046..051, 110..112) ---
    op.create_table(
        "canonical_case_decisions",
        sa.Column("decision_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "case_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cpl.cases.case_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("decision_type", sa.Text(), nullable=False),
        sa.Column("authority_context", postgresql.JSONB(), nullable=True),
        sa.Column("prior_value", postgresql.JSONB(), nullable=True),
        sa.Column("new_value", postgresql.JSONB(), nullable=True),
        sa.Column("result", sa.Text(), nullable=False),
        sa.Column("rejection_category", sa.Text(), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "supersedes_decision_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cpl.canonical_case_decisions.decision_id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.CheckConstraint(
            "decision_type IN ('CREATE', 'STATUS_TRANSITION', 'PARTICIPANT_ADD', "
            "'PARTICIPANT_REMOVE', 'METADATA_CORRECTION', 'EVENT_CORRECTION', "
            "'ASSET_REBIND_ATTEMPT')",
            name="canonical_case_decisions_type_chk",
        ),
        sa.CheckConstraint(
            "result IN ('EXECUTED', 'HOLD', 'REJECTED')",
            name="canonical_case_decisions_result_chk",
        ),
        sa.CheckConstraint(
            "rejection_category IS NULL OR rejection_category IN "
            "('AUTHORITY_REJECTION', 'SEMANTIC_REJECTION', 'UNRESOLVED', 'CONFLICT')",
            name="canonical_case_decisions_rejection_category_chk",
        ),
        schema="cpl",
    )
    op.create_index(
        "ix_canonical_case_decisions_case", "canonical_case_decisions", ["case_id"], schema="cpl",
    )

    # --- Idempotency ledger for governed Case mutations (REQ-B5-075..079, 113) ---
    op.create_table(
        "case_mutation_requests",
        sa.Column("idempotency_key", sa.Text(), primary_key=True),
        sa.Column(
            "decision_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cpl.canonical_case_decisions.decision_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        schema="cpl",
    )

    # --- CaseEvent semantic classification registry (REQ-B5-035..038, 115) ---
    # Definition-time classification, not a per-row column: satisfies
    # determinability without imposing a generic Event ontology.
    op.create_table(
        "case_event_types",
        sa.Column("event_type", sa.Text(), primary_key=True),
        sa.Column("semantic_class", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "semantic_class IN ('CPL_OPERATIONAL_FACT', 'DOMAIN_ASSERTION', "
            "'CANONICAL_DECISION_CONSEQUENCE', 'TECHNICAL_SYSTEM_EVENT')",
            name="case_event_types_semantic_class_chk",
        ),
        schema="cpl",
    )

    # --- CaseEvent correction/supersession support (REQ-B5-069..074) ---
    op.add_column(
        "case_events",
        sa.Column("event_status", sa.Text(), nullable=False, server_default="CURRENT"),
        schema="cpl",
    )
    op.add_column(
        "case_events",
        sa.Column("superseded_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        schema="cpl",
    )
    op.create_foreign_key(
        "case_events_superseded_by_id_fkey",
        "case_events",
        "case_events",
        ["superseded_by_id"],
        ["event_id"],
        source_schema="cpl",
        referent_schema="cpl",
        ondelete="RESTRICT",
    )
    op.create_check_constraint(
        "case_events_status_chk",
        "case_events",
        "event_status IN ('CURRENT', 'SUPERSEDED')",
        schema="cpl",
    )


def downgrade() -> None:
    op.drop_constraint("case_events_status_chk", "case_events", schema="cpl", type_="check")
    op.drop_constraint("case_events_superseded_by_id_fkey", "case_events", schema="cpl", type_="foreignkey")
    op.drop_column("case_events", "superseded_by_id", schema="cpl")
    op.drop_column("case_events", "event_status", schema="cpl")
    op.drop_table("case_event_types", schema="cpl")
    op.drop_table("case_mutation_requests", schema="cpl")
    op.drop_index("ix_canonical_case_decisions_case", table_name="canonical_case_decisions", schema="cpl")
    op.drop_table("canonical_case_decisions", schema="cpl")
