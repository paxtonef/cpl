"""Create B6 Execution/Artifact Governance infrastructure.

Per B6_EXECUTION_ARTIFACT_REQUIREMENT_MATRIX_v0.1.md (99 active
requirements, frozen @ 855f3c7) and the Execution Mandate
(docs/build/B6_EXECUTION_ARTIFACT_EXECUTION_MANDATE_v0.md).

`runner_governance_decisions` (REQ-B6-076..079, 061): the frozen
REQUEST -> AUTHORITY -> DECISION -> EFFECT -> HISTORY pipeline
(WHAT §25, mirroring but not copying B5's CanonicalCaseDecision — see
that model's own docstring for why B6's needs differ). `decision_mode`
distinguishes REQ-B6-076's full authority evaluation (execution
admission) from REQ-B6-015's automatic, rule-bound acceptance
(runner-reported lifecycle transitions) — this is the repaired
authority-boundary requirement (RC-B6-03/R-B6-R03) made durably
auditable, not merely asserted in code comments. `execution_id` and
`artifact_id` are both DEFERRABLE INITIALLY DEFERRED (mirroring
canonical_case_decisions.case_id, R7 pattern): admission and
registration decisions are recorded before the RunnerExecution/
RunnerArtifact row exists.

`runner_artifact_schema_definitions` (REQ-B6-089): registry of
(schema_name, schema_version) -> minimal structural contract, closing
RC-B6-07's gap. Deliberately minimal — a required-field/type list, not
a general JSON Schema engine, per the frozen "no generic Evidence
ontology / Artifact platform" exclusion (WHAT §5, REQ-B6-083).

`runner_execution_corrections` (REQ-B6-063/064): append-only log for
RunnerExecution metadata correction (category B, R-EA-W05) — the
mechanism the WHAT explicitly left to Requirements/HOW, resolved here
as append-only rather than in-place mutation, since RunnerExecution
has no dedicated schema-level correction substrate the way
RunnerArtifact does (supersedes_artifact_id).

`runner_artifacts` classification columns (REQ-B6-026..028, 090):
three orthogonal, independently NOT NULL dimensions — semantic
function, production/lifecycle role, consumption/presentation role —
implemented as attribute columns (EA-WG-01's mechanism choice,
resolved here as attribute-level rather than a separate registry
table, since the vocabularies are small and fixed by the frozen
matrix itself, not open-ended).

Revision ID: 027
Revises: 026
Create Date: 2026-09-09
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "027"
down_revision: Union[str, Sequence[str], None] = "026"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- RunnerGovernanceDecision (REQ-B6-076..079, 061, 015/077 reconciliation) ---
    op.create_table(
        "runner_governance_decisions",
        sa.Column("decision_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("decision_type", sa.Text(), nullable=False),
        sa.Column("decision_mode", sa.Text(), nullable=False),
        sa.Column(
            "execution_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cpl.runner_executions.execution_id", ondelete="RESTRICT", deferrable=True, initially="DEFERRED"),
            nullable=True,
        ),
        sa.Column(
            "artifact_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cpl.runner_artifacts.artifact_id", ondelete="RESTRICT", deferrable=True, initially="DEFERRED"),
            nullable=True,
        ),
        sa.Column("authority_context", postgresql.JSONB(), nullable=True),
        sa.Column("prior_value", postgresql.JSONB(), nullable=True),
        sa.Column("new_value", postgresql.JSONB(), nullable=True),
        sa.Column("result", sa.Text(), nullable=False),
        sa.Column("rejection_category", sa.Text(), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "decision_type IN ('EXECUTION_ADMISSION', 'EXECUTION_STATUS_TRANSITION', "
            "'ARTIFACT_REGISTRATION', 'ARTIFACT_SUPERSESSION')",
            name="runner_governance_decisions_type_chk",
        ),
        sa.CheckConstraint(
            "decision_mode IN ('AUTHORITY_EVALUATION', 'AUTOMATIC_RULE_BOUND')",
            name="runner_governance_decisions_mode_chk",
        ),
        sa.CheckConstraint(
            "result IN ('EXECUTED', 'REJECTED')",
            name="runner_governance_decisions_result_chk",
        ),
        sa.CheckConstraint(
            "rejection_category IS NULL OR rejection_category IN "
            "('AUTHORITY_REJECTION', 'SEMANTIC_REJECTION', 'UNRESOLVED', 'CONFLICT')",
            name="runner_governance_decisions_rejection_category_chk",
        ),
        sa.CheckConstraint(
            "(execution_id IS NOT NULL) OR (artifact_id IS NOT NULL)",
            name="runner_governance_decisions_target_chk",
        ),
        schema="cpl",
    )
    op.create_index("ix_runner_governance_decisions_execution", "runner_governance_decisions", ["execution_id"], schema="cpl")
    op.create_index("ix_runner_governance_decisions_artifact", "runner_governance_decisions", ["artifact_id"], schema="cpl")

    # --- Artifact schema registry (REQ-B6-089) ---
    op.create_table(
        "runner_artifact_schema_definitions",
        sa.Column("schema_name", sa.Text(), primary_key=True),
        sa.Column("schema_version", sa.Text(), primary_key=True),
        sa.Column("required_fields", postgresql.JSONB(), nullable=False),
        sa.Column("field_types", postgresql.JSONB(), nullable=False),
        sa.Column("registered_at", sa.DateTime(timezone=True), nullable=False),
        schema="cpl",
    )

    # --- Execution correction log (REQ-B6-063/064) ---
    op.create_table(
        "runner_execution_corrections",
        sa.Column("correction_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "execution_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cpl.runner_executions.execution_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("corrected_field", sa.Text(), nullable=False),
        sa.Column("prior_value", postgresql.JSONB(), nullable=True),
        sa.Column("new_value", postgresql.JSONB(), nullable=True),
        sa.Column("authority_context", postgresql.JSONB(), nullable=True),
        sa.Column("corrected_at", sa.DateTime(timezone=True), nullable=False),
        schema="cpl",
    )
    op.create_index("ix_runner_execution_corrections_execution", "runner_execution_corrections", ["execution_id"], schema="cpl")

    # --- Artifact multidimensional classification (REQ-B6-026..028, 090) ---
    op.add_column("runner_artifacts", sa.Column("semantic_function", sa.Text(), nullable=True), schema="cpl")
    op.add_column("runner_artifacts", sa.Column("lifecycle_role", sa.Text(), nullable=True), schema="cpl")
    op.add_column("runner_artifacts", sa.Column("presentation_role", sa.Text(), nullable=True), schema="cpl")
    op.create_check_constraint(
        "runner_artifacts_semantic_function_chk",
        "runner_artifacts",
        "semantic_function IS NULL OR semantic_function IN "
        "('EXECUTION_OUTPUT_CARRIER', 'EXECUTION_EVIDENCE_CARRIER', 'DOMAIN_ASSERTION_CARRIER', "
        "'DOMAIN_DETERMINATION_CARRIER', 'TECHNICAL_OPERATIONAL_MATERIAL')",
        schema="cpl",
    )
    op.create_check_constraint(
        "runner_artifacts_lifecycle_role_chk",
        "runner_artifacts",
        "lifecycle_role IS NULL OR lifecycle_role IN ('INTERMEDIATE', 'FINAL')",
        schema="cpl",
    )
    op.create_check_constraint(
        "runner_artifacts_presentation_role_chk",
        "runner_artifacts",
        "presentation_role IS NULL OR presentation_role IN ('INTERNAL', 'PRODUCT_DISPLAYABLE')",
        schema="cpl",
    )
    # Columns are added nullable (existing-row safety per Alembic convention used
    # throughout 001-026), then the frozen mandatoriness requirement (REQ-B6-090) is
    # enforced by the application-layer registration path, which never permits a
    # canonical registration to complete with any of the three unset. The table has
    # zero rows at this baseline (no B6 service layer existed before this migration),
    # so a NOT NULL constraint could have been used safely — nullable is chosen instead
    # to keep the migration itself independent of application-layer registration
    # ordering, and because a future direct-SQL administrative correction path should
    # not be blocked by a NOT NULL it cannot yet satisfy mid-correction.


def downgrade() -> None:
    op.drop_constraint("runner_artifacts_presentation_role_chk", "runner_artifacts", schema="cpl", type_="check")
    op.drop_constraint("runner_artifacts_lifecycle_role_chk", "runner_artifacts", schema="cpl", type_="check")
    op.drop_constraint("runner_artifacts_semantic_function_chk", "runner_artifacts", schema="cpl", type_="check")
    op.drop_column("runner_artifacts", "presentation_role", schema="cpl")
    op.drop_column("runner_artifacts", "lifecycle_role", schema="cpl")
    op.drop_column("runner_artifacts", "semantic_function", schema="cpl")
    op.drop_index("ix_runner_execution_corrections_execution", table_name="runner_execution_corrections", schema="cpl")
    op.drop_table("runner_execution_corrections", schema="cpl")
    op.drop_table("runner_artifact_schema_definitions", schema="cpl")
    op.drop_index("ix_runner_governance_decisions_artifact", table_name="runner_governance_decisions", schema="cpl")
    op.drop_index("ix_runner_governance_decisions_execution", table_name="runner_governance_decisions", schema="cpl")
    op.drop_table("runner_governance_decisions", schema="cpl")
