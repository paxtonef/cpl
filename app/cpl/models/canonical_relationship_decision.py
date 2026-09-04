from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base import Base


class CanonicalRelationshipDecision(Base):
    """Durable governed record of a material ContactAssetRelationship
    mutation (REQ-B4-120..132). ESTABLISH/END/CORRECT/SUPERSEDE remain
    semantically distinct decision types; valid_from/valid_until track
    the frozen VALID TIME distinct from decided_at (CPL DECISION TIME)."""

    __tablename__ = "canonical_relationship_decisions"
    __table_args__ = (
        CheckConstraint("decision_type IN ('ESTABLISH', 'END', 'CORRECT', 'SUPERSEDE')", name="canonical_relationship_decisions_type_chk"),
        CheckConstraint("result IN ('EXECUTED', 'HOLD', 'REJECTED')", name="canonical_relationship_decisions_result_chk"),
        {"schema": "cpl"},
    )

    decision_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    relationship_id = Column(UUID(as_uuid=True), ForeignKey("cpl.contact_asset_relationships.relationship_id", ondelete="RESTRICT"), nullable=False)
    decision_type = Column(Text, nullable=False)
    evidence = Column(JSONB, nullable=True)
    authority_context = Column(JSONB, nullable=True)
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)
    decided_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    result = Column(Text, nullable=False)
    supersedes_decision_id = Column(UUID(as_uuid=True), ForeignKey("cpl.canonical_relationship_decisions.decision_id", ondelete="RESTRICT"), nullable=True)
