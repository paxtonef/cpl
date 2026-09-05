from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class RelationshipMutationRequest(Base):
    """Idempotency ledger for governed relationship canonical mutation
    requests (REQ-B4-252, REQ-B4-253, REQ-B4-254). Payload similarity
    alone MUST NOT establish idempotency identity — only a matching
    governed idempotency_key does."""

    __tablename__ = "relationship_mutation_requests"
    __table_args__ = {"schema": "cpl"}

    idempotency_key = Column(Text, primary_key=True)
    decision_id = Column(UUID(as_uuid=True), ForeignKey("cpl.canonical_relationship_decisions.decision_id", ondelete="RESTRICT"), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
