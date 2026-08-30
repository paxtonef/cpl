from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, CheckConstraint, Boolean
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class ContactPoint(Base):
    __tablename__ = "contact_points"
    __table_args__ = (
        CheckConstraint("point_type IN ('EMAIL', 'PHONE')", name="contact_points_type_chk"),
        CheckConstraint("verification_status IN ('UNVERIFIED', 'PENDING', 'VERIFIED', 'FAILED', 'REVOKED')", name="contact_points_verification_chk"),
        CheckConstraint("valid_until IS NULL OR valid_until >= valid_from", name="contact_points_validity_chk"),
        {"schema": "cpl"},
    )

    contact_point_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("cpl.contacts.contact_id", ondelete="RESTRICT"), nullable=False)
    point_type = Column(Text, nullable=False)
    raw_value = Column(Text, nullable=False)
    normalized_value = Column(Text, nullable=False)
    verification_status = Column(Text, nullable=False, default="UNVERIFIED")
    is_primary = Column(Boolean, nullable=False, default=False)
    valid_from = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    valid_until = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
