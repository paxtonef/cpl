from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base import Base


class RunnerArtifact(Base):
    """B6-extended (REQ-B6-026..028, 090): three classification columns
    added below (semantic_function, lifecycle_role, presentation_role).
    All B2-era columns/constraints above this docstring are unchanged
    and were verified ALIGNED against the frozen requirement matrix's
    own §31/§36 substrate classification — nothing about the original
    B2 shape needed repair."""

    __tablename__ = "runner_artifacts"
    __table_args__ = (
        CheckConstraint("artifact_status IN ('CREATED', 'VALIDATED', 'SUPERSEDED', 'REJECTED')", name="runner_artifacts_status_chk"),
        CheckConstraint("supersedes_artifact_id IS NULL OR supersedes_artifact_id <> artifact_id", name="runner_artifacts_not_self_superseded_chk"),
        CheckConstraint(
            "(hash_algorithm IS NULL AND content_hash IS NULL) OR (hash_algorithm IS NOT NULL AND content_hash IS NOT NULL)",
            name="runner_artifacts_hash_pair_chk",
        ),
        CheckConstraint(
            "semantic_function IS NULL OR semantic_function IN "
            "('EXECUTION_OUTPUT_CARRIER', 'EXECUTION_EVIDENCE_CARRIER', 'DOMAIN_ASSERTION_CARRIER', "
            "'DOMAIN_DETERMINATION_CARRIER', 'TECHNICAL_OPERATIONAL_MATERIAL')",
            name="runner_artifacts_semantic_function_chk",
        ),
        CheckConstraint("lifecycle_role IS NULL OR lifecycle_role IN ('INTERMEDIATE', 'FINAL')", name="runner_artifacts_lifecycle_role_chk"),
        CheckConstraint(
            "presentation_role IS NULL OR presentation_role IN ('INTERNAL', 'PRODUCT_DISPLAYABLE')",
            name="runner_artifacts_presentation_role_chk",
        ),
        {"schema": "cpl"},
    )

    artifact_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    execution_id = Column(UUID(as_uuid=True), ForeignKey("cpl.runner_executions.execution_id", ondelete="RESTRICT"), nullable=False)
    artifact_type = Column(Text, nullable=False)
    schema_name = Column(Text, nullable=False)
    schema_version = Column(Text, nullable=False)
    artifact_status = Column(Text, nullable=False, default="CREATED")
    payload = Column(JSONB, nullable=False)
    hash_algorithm = Column(Text, nullable=True)
    content_hash = Column(Text, nullable=True)
    supersedes_artifact_id = Column(UUID(as_uuid=True), ForeignKey("cpl.runner_artifacts.artifact_id", ondelete="RESTRICT"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    # B6 classification dimensions (REQ-B6-026..028, 090). Nullable at the
    # schema level (existing-row safety per the 001-026 migration convention);
    # mandatoriness (all three set, non-NULL) is enforced by the application
    # registration path (app.cpl.runners.classification), never by the column
    # definition alone — see REQ-B6-090's five-outcome validation taxonomy.
    semantic_function = Column(Text, nullable=True)
    lifecycle_role = Column(Text, nullable=True)
    presentation_role = Column(Text, nullable=True)
