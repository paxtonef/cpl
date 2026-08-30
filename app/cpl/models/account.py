from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        CheckConstraint("account_status IN ('PENDING', 'ACTIVE', 'DISABLED', 'REVOKED')", name="accounts_status_chk"),
        UniqueConstraint("auth_provider", "provider_subject_id", name="accounts_provider_identity_uq"),
        {"schema": "cpl"},
    )

    account_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("cpl.contacts.contact_id", ondelete="RESTRICT"), nullable=False)
    auth_provider = Column(Text, nullable=False)
    provider_subject_id = Column(Text, nullable=False)
    account_status = Column(Text, nullable=False, default="PENDING")
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    last_authenticated_at = Column(DateTime(timezone=True), nullable=True)
    disabled_at = Column(DateTime(timezone=True), nullable=True)
