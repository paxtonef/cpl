from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class ContactCreationRequest(Base):
    """Idempotency ledger for create_contact (REQ-B3-067, REQ-B3-124/125)."""

    __tablename__ = "contact_creation_requests"
    __table_args__ = {"schema": "cpl"}

    idempotency_key = Column(Text, primary_key=True)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("cpl.contacts.contact_id", ondelete="RESTRICT"), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
