from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime, ForeignKey, CheckConstraint, Integer, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class Case(Base):
    __tablename__ = "cases"
    __table_args__ = (
        CheckConstraint("case_status IN ('OPEN', 'IN_PROGRESS', 'WAITING_FOR_USER', 'WAITING_FOR_EXTERNAL_INFORMATION', 'RESOLVED', 'CLOSED', 'REOPENED', 'CANCELLED')", name="cases_status_chk"),
        CheckConstraint("case_status <> 'CLOSED' OR closed_at IS NOT NULL", name="cases_closed_at_chk"),
        {"schema": "cpl"},
    )

    case_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    primary_contact_id = Column(UUID(as_uuid=True), ForeignKey("cpl.contacts.contact_id", ondelete="RESTRICT"), nullable=False)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("cpl.assets.asset_id", ondelete="RESTRICT"), nullable=False)
    domain = Column(Text, nullable=False)
    case_type = Column(Text, nullable=False)
    case_status = Column(Text, nullable=False, default="OPEN")
    title = Column(Text)
    current_execution_id = Column(UUID(as_uuid=True), ForeignKey("cpl.runner_executions.execution_id", ondelete="RESTRICT"), nullable=True)
    opened_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    closed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    record_version = Column(BigInteger, nullable=False, default=0)
