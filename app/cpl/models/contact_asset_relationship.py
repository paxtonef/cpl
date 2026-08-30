from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime, ForeignKey, CheckConstraint, Integer, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class ContactAssetRelationship(Base):
    __tablename__ = "contact_asset_relationships"
    __table_args__ = (
        CheckConstraint("relationship_status IN ('UNVERIFIED', 'ACTIVE', 'DISPUTED', 'ENDED')", name="contact_asset_relationships_status_chk"),
        CheckConstraint("valid_until IS NULL OR valid_from IS NULL OR valid_until >= valid_from", name="contact_asset_relationships_validity_chk"),
        {"schema": "cpl"},
    )

    relationship_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("cpl.contacts.contact_id", ondelete="RESTRICT"), nullable=False)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("cpl.assets.asset_id", ondelete="RESTRICT"), nullable=False)
    relationship_type = Column(Text, nullable=False)
    relationship_status = Column(Text, nullable=False, default="UNVERIFIED")
    source = Column(Text)
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    record_version = Column(BigInteger, nullable=False, default=0)
