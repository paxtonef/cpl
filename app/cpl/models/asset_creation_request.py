from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class AssetCreationRequest(Base):
    """Idempotency ledger for create_asset (REQ-B4-012/013, mirrors
    B3's ContactCreationRequest)."""

    __tablename__ = "asset_creation_requests"
    __table_args__ = {"schema": "cpl"}

    idempotency_key = Column(Text, primary_key=True)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("cpl.assets.asset_id", ondelete="RESTRICT"), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
