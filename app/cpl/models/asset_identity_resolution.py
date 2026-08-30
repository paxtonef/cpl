from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime, ForeignKey, CheckConstraint, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base import Base


class AssetIdentityResolution(Base):
    __tablename__ = "asset_identity_resolutions"
    __table_args__ = (
        CheckConstraint("resolution_status IN ('RESOLVED', 'PARTIALLY_RESOLVED', 'AMBIGUOUS', 'CONTRADICTORY', 'UNRESOLVED', 'FAILED')", name="asset_identity_resolutions_status_chk"),
        CheckConstraint("confidence IS NULL OR (confidence >= 0 AND confidence <= 1)", name="asset_identity_resolutions_confidence_chk"),
        CheckConstraint("supersedes_resolution_id IS NULL OR supersedes_resolution_id <> resolution_id", name="asset_identity_resolutions_not_self_superseded_chk"),
        {"schema": "cpl"},
    )

    resolution_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("cpl.assets.asset_id", ondelete="RESTRICT"), nullable=False)
    resolver_type = Column(Text, nullable=False)
    resolver_version = Column(Text, nullable=False)
    execution_id = Column(UUID(as_uuid=True), ForeignKey("cpl.runner_executions.execution_id", ondelete="RESTRICT"), nullable=True)
    resolution_status = Column(Text, nullable=False)
    confidence = Column(Numeric(5, 4), nullable=True)
    canonical_identity_payload = Column(JSONB, nullable=False)
    provenance_payload = Column(JSONB, nullable=True)
    supersedes_resolution_id = Column(UUID(as_uuid=True), ForeignKey("cpl.asset_identity_resolutions.resolution_id", ondelete="RESTRICT"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime(timezone=True), nullable=True)
