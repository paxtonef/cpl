from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base import Base


class RunnerArtifact(Base):
    __tablename__ = "runner_artifacts"
    __table_args__ = (
        CheckConstraint("artifact_status IN ('CREATED', 'VALIDATED', 'SUPERSEDED', 'REJECTED')", name="runner_artifacts_status_chk"),
        CheckConstraint("supersedes_artifact_id IS NULL OR supersedes_artifact_id <> artifact_id", name="runner_artifacts_not_self_superseded_chk"),
        CheckConstraint(
            "(hash_algorithm IS NULL AND content_hash IS NULL) OR (hash_algorithm IS NOT NULL AND content_hash IS NOT NULL)",
            name="runner_artifacts_hash_pair_chk",
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
