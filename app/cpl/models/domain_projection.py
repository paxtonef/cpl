from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base import Base


class DomainProjection(Base):
    """Generic B4 governance record for a domain-specific Asset
    projection (REQ-B4-096..103). Governs attachment/continuity/
    history only; substantive domain payload semantics (e.g. VIR's
    VehicleDetail) remain outside generic CPL (B4-CI... boundary,
    mandate Sec. 8/24)."""

    __tablename__ = "domain_projections"
    __table_args__ = (
        CheckConstraint(
            "projection_status IN ('ATTACHED', 'CURRENT', 'SUPERSEDED', 'HISTORICAL', 'DISPUTED')",
            name="domain_projections_status_chk",
        ),
        {"schema": "cpl"},
    )

    projection_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("cpl.assets.asset_id", ondelete="RESTRICT"), nullable=False)
    projection_type = Column(Text, nullable=False)
    projection_status = Column(Text, nullable=False, default="CURRENT")
    payload = Column(JSONB, nullable=True)
    domain_authority = Column(Text, nullable=True)
    source_resolution_id = Column(UUID(as_uuid=True), ForeignKey("cpl.asset_identity_resolutions.resolution_id", ondelete="RESTRICT"), nullable=True)
    supersedes_projection_id = Column(UUID(as_uuid=True), ForeignKey("cpl.domain_projections.projection_id", ondelete="RESTRICT"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
