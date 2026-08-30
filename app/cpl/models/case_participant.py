from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class CaseParticipant(Base):
    __tablename__ = "case_participants"
    __table_args__ = (
        CheckConstraint("participant_status IN ('ACTIVE', 'LEFT', 'REMOVED')", name="case_participants_status_chk"),
        CheckConstraint("left_at IS NULL OR left_at >= joined_at", name="case_participants_time_chk"),
        {"schema": "cpl"},
    )

    case_participant_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cpl.cases.case_id", ondelete="RESTRICT"), nullable=False)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("cpl.contacts.contact_id", ondelete="RESTRICT"), nullable=False)
    participant_role = Column(Text, nullable=False)
    participant_status = Column(Text, nullable=False, default="ACTIVE")
    joined_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    left_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
