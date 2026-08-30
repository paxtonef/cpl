from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime, ForeignKey, CheckConstraint, Integer, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class Asset(Base):
    __tablename__ = "assets"
    __table_args__ = (
        CheckConstraint("asset_status IN ('UNKNOWN', 'ACTIVE', 'INACTIVE', 'DISPOSED', 'ARCHIVED')", name="assets_status_chk"),
        {"schema": "cpl"},
    )

    asset_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    asset_domain = Column(Text, nullable=False)
    asset_type = Column(Text, nullable=False)
    asset_status = Column(Text, nullable=False, default="UNKNOWN")
    display_name = Column(Text)
    current_identity_resolution_id = Column(UUID(as_uuid=True), ForeignKey("cpl.asset_identity_resolutions.resolution_id", ondelete="RESTRICT"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    archived_at = Column(DateTime(timezone=True), nullable=True)
    record_version = Column(BigInteger, nullable=False, default=0)
