from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class AssetMergeRequest(Base):
    """Idempotency ledger for governed Asset merge/correction requests
    (REQ-B4-250, REQ-B4-251, REQ-B4-253, REQ-B4-254). Replay of the
    same idempotency_key MUST NOT create a second independent
    canonical transition — it returns the original decision."""

    __tablename__ = "asset_merge_requests"
    __table_args__ = {"schema": "cpl"}

    idempotency_key = Column(Text, primary_key=True)
    decision_id = Column(UUID(as_uuid=True), ForeignKey("cpl.canonical_asset_identity_decisions.decision_id", ondelete="RESTRICT"), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
