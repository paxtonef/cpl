from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base import Base


class RunnerExecutionCorrection(Base):
    """Append-only log of RunnerExecution metadata corrections
    (REQ-B6-063 category B, R-EA-W05). Unlike RunnerArtifact,
    RunnerExecution has no dedicated schema-level correction substrate
    (no supersedes_artifact_id analogue) — this table is the
    Requirements/HOW-level mechanism the WHAT explicitly left open,
    resolved as append-only rather than in-place mutation of historical
    execution fields (REQ-B6-062: a historical RunnerExecution
    occurrence must never be rewritten as if a different execution
    happened). Non-occurrence metadata only (e.g., a mis-recorded
    execution_purpose) — never execution_status, never identity."""

    __tablename__ = "runner_execution_corrections"
    __table_args__ = {"schema": "cpl"}

    correction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    execution_id = Column(UUID(as_uuid=True), ForeignKey("cpl.runner_executions.execution_id", ondelete="RESTRICT"), nullable=False)
    corrected_field = Column(Text, nullable=False)
    prior_value = Column(JSONB, nullable=True)
    new_value = Column(JSONB, nullable=True)
    authority_context = Column(JSONB, nullable=True)
    corrected_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
