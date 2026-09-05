from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base import Base


class CanonicalAssetIdentityDecision(Base):
    """Durable governed record of a canonical Asset identity decision
    (REQ-B4-037..046). Distinct from AssetIdentityResolution: the
    resolution is what domain authority determined about physical
    identity; this decision is what CPL authorized as canonical
    representation (B4_WHAT_CONSOLIDATION_v0.1 Sec. 9)."""

    __tablename__ = "canonical_asset_identity_decisions"
    __table_args__ = (
        CheckConstraint("decision_type IN ('MERGE', 'CORRECTION')", name="canonical_asset_identity_decisions_type_chk"),
        CheckConstraint("result IN ('EXECUTED', 'HOLD', 'REJECTED')", name="canonical_asset_identity_decisions_result_chk"),
        CheckConstraint("source_asset_id <> target_asset_id", name="canonical_asset_identity_decisions_not_self_chk"),
        {"schema": "cpl"},
    )

    decision_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    decision_type = Column(Text, nullable=False)
    source_asset_id = Column(UUID(as_uuid=True), ForeignKey("cpl.assets.asset_id", ondelete="RESTRICT"), nullable=False)
    target_asset_id = Column(UUID(as_uuid=True), ForeignKey("cpl.assets.asset_id", ondelete="RESTRICT"), nullable=False)
    resolution_id = Column(UUID(as_uuid=True), ForeignKey("cpl.asset_identity_resolutions.resolution_id", ondelete="RESTRICT"), nullable=True)
    survivor_rule_applied = Column(Text, nullable=True)
    survivor_override_reason = Column(Text, nullable=True)
    dependency_disposition = Column(JSONB, nullable=True)
    authority_context = Column(JSONB, nullable=True)
    result = Column(Text, nullable=False)
    decided_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    supersedes_decision_id = Column(UUID(as_uuid=True), ForeignKey("cpl.canonical_asset_identity_decisions.decision_id", ondelete="RESTRICT"), nullable=True)
