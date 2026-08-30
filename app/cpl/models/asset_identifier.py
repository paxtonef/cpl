from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime, ForeignKey, CheckConstraint, Numeric
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class AssetIdentifier(Base):
    __tablename__ = "asset_identifiers"
    __table_args__ = (
        CheckConstraint("identifier_status IN ('OBSERVED', 'VERIFIED', 'DISPUTED', 'SUPERSEDED', 'INVALIDATED')", name="asset_identifiers_status_chk"),
        CheckConstraint("confidence IS NULL OR (confidence >= 0 AND confidence <= 1)", name="asset_identifiers_confidence_chk"),
        CheckConstraint("valid_until IS NULL OR valid_from IS NULL OR valid_until >= valid_from", name="asset_identifiers_validity_chk"),
        {"schema": "cpl"},
    )

    asset_identifier_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("cpl.assets.asset_id", ondelete="RESTRICT"), nullable=False)
    identifier_type = Column(Text, nullable=False)
    identifier_value = Column(Text, nullable=False)
    normalized_value = Column(Text)
    country = Column(Text)
    source = Column(Text)
    confidence = Column(Numeric(5, 4), nullable=True)
    identifier_status = Column(Text, nullable=False, default="OBSERVED")
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
