from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class CaseMutationRequest(Base):
    """Idempotency ledger for governed Case mutation requests
    (REQ-B5-075..079, 113). Replay of the same idempotency_key MUST
    NOT create a second independent canonical transition — it returns
    the original decision."""

    __tablename__ = "case_mutation_requests"
    __table_args__ = {"schema": "cpl"}

    idempotency_key = Column(Text, primary_key=True)
    decision_id = Column(UUID(as_uuid=True), ForeignKey("cpl.canonical_case_decisions.decision_id", ondelete="RESTRICT"), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
