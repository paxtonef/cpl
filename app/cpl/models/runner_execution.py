from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class RunnerExecution(Base):
    __tablename__ = "runner_executions"
    __table_args__ = (
        CheckConstraint("execution_status IN ('CREATED', 'QUEUED', 'RUNNING', 'COMPLETED', 'FAILED', 'BLOCKED', 'CANCELLED')", name="runner_executions_status_chk"),
        CheckConstraint("parent_execution_id IS NULL OR parent_execution_id <> execution_id", name="runner_executions_not_self_parent_chk"),
        CheckConstraint("completed_at IS NULL OR started_at IS NULL OR completed_at >= started_at", name="runner_executions_time_chk"),
        CheckConstraint("execution_status <> 'COMPLETED' OR completed_at IS NOT NULL", name="runner_executions_completed_at_chk"),
        {"schema": "cpl"},
    )

    execution_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cpl.cases.case_id", ondelete="RESTRICT"), nullable=False)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("cpl.assets.asset_id", ondelete="RESTRICT"), nullable=False)
    runner_type = Column(Text, nullable=False)
    runner_version = Column(Text, nullable=False)
    execution_purpose = Column(Text, nullable=True)
    execution_status = Column(Text, nullable=False, default="CREATED")
    parent_execution_id = Column(UUID(as_uuid=True), ForeignKey("cpl.runner_executions.execution_id", ondelete="RESTRICT"), nullable=True)
    initiated_by_contact_id = Column(UUID(as_uuid=True), ForeignKey("cpl.contacts.contact_id", ondelete="RESTRICT"), nullable=True)
    idempotency_key = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
