from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base import Base


class MergeProposal(Base):
    """Durable PROPOSE_MERGE artifact (REQ-B3-042/043/044)."""

    __tablename__ = "merge_proposals"
    __table_args__ = (
        CheckConstraint("status IN ('PROPOSED', 'AUTHORIZED', 'EXECUTED', 'REJECTED')", name="merge_proposals_status_chk"),
        CheckConstraint("source_contact_id <> target_contact_id", name="merge_proposals_not_self_chk"),
        {"schema": "cpl"},
    )

    proposal_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    source_contact_id = Column(UUID(as_uuid=True), ForeignKey("cpl.contacts.contact_id", ondelete="RESTRICT"), nullable=False)
    target_contact_id = Column(UUID(as_uuid=True), ForeignKey("cpl.contacts.contact_id", ondelete="RESTRICT"), nullable=False)
    reason = Column(Text, nullable=True)
    evidence = Column(JSONB, nullable=True)
    proposed_by = Column(Text, nullable=True)
    status = Column(Text, nullable=False, default="PROPOSED")
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime(timezone=True), nullable=True)
