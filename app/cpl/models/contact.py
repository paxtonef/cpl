from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, CheckConstraint, Integer, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class Contact(Base):
    __tablename__ = "contacts"
    __table_args__ = (
        CheckConstraint("contact_type IN ('PERSON', 'ORGANIZATION')", name="contacts_type_chk"),
        CheckConstraint("contact_status IN ('ACTIVE', 'MERGED', 'BLOCKED', 'ARCHIVED')", name="contacts_status_chk"),
        CheckConstraint("merged_into_id IS NULL OR merged_into_id <> contact_id", name="contacts_not_self_merged_chk"),
        CheckConstraint("contact_status <> 'MERGED' OR merged_into_id IS NOT NULL", name="contacts_merged_target_required_chk"),
        {"schema": "cpl"},
    )

    contact_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    contact_type = Column(Text, nullable=False)
    display_name = Column(Text)
    first_name = Column(Text)
    last_name = Column(Text)
    contact_status = Column(Text, nullable=False, default="ACTIVE")
    merged_into_id = Column(UUID(as_uuid=True), ForeignKey("cpl.contacts.contact_id", ondelete="RESTRICT"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    archived_at = Column(DateTime(timezone=True), nullable=True)
    record_version = Column(BigInteger, nullable=False, default=0)
