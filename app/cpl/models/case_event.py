from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base import Base


class CaseEvent(Base):
    __tablename__ = "case_events"
    __table_args__ = (
        CheckConstraint("actor_type IN ('CONTACT', 'SYSTEM', 'RUNNER', 'ADMIN', 'EXTERNAL_PARTY')", name="case_events_actor_type_chk"),
        {"schema": "cpl"},
    )

    event_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cpl.cases.case_id", ondelete="RESTRICT"), nullable=False)
    event_type = Column(Text, nullable=False)
    actor_type = Column(Text, nullable=False)
    actor_reference_id = Column(UUID(as_uuid=True), nullable=True)
    execution_id = Column(UUID(as_uuid=True), ForeignKey("cpl.runner_executions.execution_id", ondelete="RESTRICT"), nullable=True)
    occurred_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    payload = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
