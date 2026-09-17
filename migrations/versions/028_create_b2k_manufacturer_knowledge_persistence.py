"""Create B2-K manufacturer knowledge persistence (non-execution-scoped).

B2-K KNOWLEDGE PERSISTENCE IMPLEMENTATION MANDATE v1, §14/§15. Persists
reusable manufacturer-documented dashboard knowledge (e.g. the corrected,
verified Peugeot 3008 II fixture) independent of any diagnostic
execution/case -- deliberately NOT an extension of `runner_artifacts`,
whose `execution_id` is NOT NULL and therefore structurally forces every
row to belong to exactly one diagnostic case (confirmed by direct read
during the B2-K Knowledge Persistence Investigation). Reusing that table
would falsely make one diagnostic execution the owner of knowledge meant
to be shared across many future cases -- forbidden by the investigation's
own explicit finding and by this mandate's §3.

`manufacturer_knowledge_documents`: one row per manufacturer document
generation. `lifecycle_status` distinguishes currently-usable ('ACTIVE')
from historically-retained ('SUPERSEDED') knowledge -- append-only in
spirit: a new generation never overwrites an old row, it is inserted
alongside it with `supersedes_document_row_id` pointing back, and the old
row's own `lifecycle_status` flips to SUPERSEDED. `applicability_
manufacturer/model/generation` are the vehicle-family lookup key (mirrors
pgdr.domain.dashboard_knowledge.VehicleApplicabilityContext's own
manufacturer/model/generation fields); date-based applicability
(first-registration-period-dependent edition selection, per Peugeot's
own documented rule) stays in `applicability_period_start/end/note`,
deliberately left NULL for the POC seed since the supplied source did not
establish this specific document's own date boundary (no boundary is
fabricated). `content_hash` supports deterministic, idempotent seeding:
re-running the seed with byte-identical content must not create a
duplicate ACTIVE generation.

`manufacturer_knowledge_dashboard_entries`: one row per
DashboardReferenceEntry, FK'd to its parent document. No execution_id,
case_id, or diagnostic_id column exists on either table -- case/execution
data and manufacturer knowledge remain structurally separate, per the
investigation's own CASE DATA SEPARATION finding.

Revision ID: 028
Revises: 027
Create Date: 2026-09-16
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "028"
down_revision: Union[str, Sequence[str], None] = "027"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "manufacturer_knowledge_documents",
        sa.Column("document_row_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("manufacturer", sa.Text(), nullable=False),
        sa.Column("document_id", sa.Text(), nullable=False),
        sa.Column("document_title", sa.Text(), nullable=False),
        sa.Column("edition", sa.Text(), nullable=True),
        sa.Column("applicability_manufacturer", sa.Text(), nullable=False),
        sa.Column("applicability_model", sa.Text(), nullable=False),
        sa.Column("applicability_generation", sa.Text(), nullable=False),
        sa.Column("applicability_period_start", sa.Text(), nullable=True),
        sa.Column("applicability_period_end", sa.Text(), nullable=True),
        sa.Column("applicability_period_note", sa.Text(), nullable=True),
        sa.Column("source_authority", sa.Text(), nullable=False),
        sa.Column("source_locator", sa.Text(), nullable=False),
        sa.Column("lifecycle_status", sa.Text(), nullable=False, server_default="ACTIVE"),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "supersedes_document_row_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cpl.manufacturer_knowledge_documents.document_row_id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column("content_hash", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("lifecycle_status IN ('ACTIVE', 'SUPERSEDED')", name="mfr_knowledge_documents_lifecycle_chk"),
        sa.CheckConstraint(
            "source_authority IN ('manufacturer_official', 'unverified_placeholder')",
            name="mfr_knowledge_documents_source_authority_chk",
        ),
        sa.CheckConstraint(
            "supersedes_document_row_id IS NULL OR supersedes_document_row_id <> document_row_id",
            name="mfr_knowledge_documents_not_self_superseded_chk",
        ),
        schema="cpl",
    )
    op.create_index(
        "ix_mfr_knowledge_documents_applicability",
        "manufacturer_knowledge_documents",
        ["applicability_manufacturer", "applicability_model", "applicability_generation", "lifecycle_status"],
        schema="cpl",
    )
    op.create_index(
        "ix_mfr_knowledge_documents_document_id",
        "manufacturer_knowledge_documents", ["document_id"], schema="cpl",
    )

    op.create_table(
        "manufacturer_knowledge_dashboard_entries",
        sa.Column("entry_row_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "document_row_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cpl.manufacturer_knowledge_documents.document_row_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("entry_id", sa.Text(), nullable=False),
        sa.Column("manufacturer_designation", sa.Text(), nullable=False),
        sa.Column("symbol_descriptor", sa.Text(), nullable=True),
        sa.Column("colour", sa.Text(), nullable=True),
        sa.Column("state", sa.Text(), nullable=True),
        sa.Column("displayed_message", sa.Text(), nullable=True),
        sa.Column("audible_signal", sa.Text(), nullable=True),
        sa.Column("documented_meaning", sa.Text(), nullable=False),
        sa.Column("documented_instruction", sa.Text(), nullable=True),
        sa.Column("combined_with_entry_ids", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "state IS NULL OR state IN ('fixed', 'flashing', 'unknown')",
            name="mfr_knowledge_entries_state_chk",
        ),
        schema="cpl",
    )
    op.create_index(
        "ix_mfr_knowledge_entries_document",
        "manufacturer_knowledge_dashboard_entries", ["document_row_id"], schema="cpl",
    )


def downgrade() -> None:
    op.drop_index("ix_mfr_knowledge_entries_document", table_name="manufacturer_knowledge_dashboard_entries", schema="cpl")
    op.drop_table("manufacturer_knowledge_dashboard_entries", schema="cpl")
    op.drop_index("ix_mfr_knowledge_documents_document_id", table_name="manufacturer_knowledge_documents", schema="cpl")
    op.drop_index("ix_mfr_knowledge_documents_applicability", table_name="manufacturer_knowledge_documents", schema="cpl")
    op.drop_table("manufacturer_knowledge_documents", schema="cpl")
