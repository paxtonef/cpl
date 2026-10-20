from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base import Base


class RunnerArtifactRedaction(Base):
    """Trace of the governed expurgation of one RunnerArtifact (REQ-B6-091,
    migration 030). One row per artifact, never updated: the operation that
    removed the vehicle identifiers, its reason, its opaque operator
    reference, the content hash recorded at registration (historical trace)
    and the hash of the content that remains. The removed locations are
    named, never their values; no copy of the removed content is kept."""

    __tablename__ = "runner_artifact_redactions"
    __table_args__ = (
        CheckConstraint("operation = 'VEHICLE_IDENTIFIER_REDACTION'", name="runner_artifact_redactions_operation_chk"),
        CheckConstraint("reason IN ('RETENTION_POLICY', 'DATA_SUBJECT_REQUEST')", name="runner_artifact_redactions_reason_chk"),
        CheckConstraint(
            "(original_hash_algorithm IS NULL AND original_content_hash IS NULL) OR "
            "(original_hash_algorithm IS NOT NULL AND original_content_hash IS NOT NULL)",
            name="runner_artifact_redactions_original_hash_pair_chk",
        ),
        {"schema": "cpl"},
    )

    artifact_id = Column(UUID(as_uuid=True), ForeignKey("cpl.runner_artifacts.artifact_id", ondelete="RESTRICT"), primary_key=True)
    decision_id = Column(UUID(as_uuid=True), ForeignKey("cpl.runner_governance_decisions.decision_id", ondelete="RESTRICT"), nullable=False)
    operation_id = Column(UUID(as_uuid=True), nullable=False, default=uuid4)
    operation = Column(Text, nullable=False, default="VEHICLE_IDENTIFIER_REDACTION")
    reason = Column(Text, nullable=False)
    operator_reference = Column(Text, nullable=False)
    redacted_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    original_hash_algorithm = Column(Text, nullable=True)
    original_content_hash = Column(Text, nullable=True)
    hash_algorithm = Column(Text, nullable=False)
    redacted_content_hash = Column(Text, nullable=False)
    redacted_locations = Column(JSONB, nullable=False)
