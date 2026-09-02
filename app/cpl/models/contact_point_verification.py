from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base import Base


class ContactPointVerification(Base):
    """Durable Verification Assertion record (REQ-B3-116..120, REQ-B3-078)."""

    __tablename__ = "contact_point_verifications"
    __table_args__ = (
        CheckConstraint("result IN ('ACCEPTED', 'REJECTED')", name="cp_verifications_result_chk"),
        {"schema": "cpl"},
    )

    verification_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    contact_point_id = Column(UUID(as_uuid=True), ForeignKey("cpl.contact_points.contact_point_id", ondelete="RESTRICT"), nullable=False)
    verification_class = Column(Text, nullable=False)
    issuer = Column(Text, nullable=False)
    result = Column(Text, nullable=False)
    verified_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    authority_context = Column(JSONB, nullable=True)
    replay_key = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
