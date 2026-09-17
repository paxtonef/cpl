"""B2-K KNOWLEDGE PERSISTENCE IMPLEMENTATION MANDATE v1, §14. One row per
DashboardReferenceEntry, FK'd to its parent ManufacturerKnowledgeDocument.
No execution_id/case_id column anywhere on this model -- see migration
028's own docstring for why."""
from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base import Base


class ManufacturerKnowledgeDashboardEntry(Base):
    __tablename__ = "manufacturer_knowledge_dashboard_entries"
    __table_args__ = (
        CheckConstraint("state IS NULL OR state IN ('fixed', 'flashing', 'unknown')", name="mfr_knowledge_entries_state_chk"),
        {"schema": "cpl"},
    )

    entry_row_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_row_id = Column(
        UUID(as_uuid=True), ForeignKey("cpl.manufacturer_knowledge_documents.document_row_id", ondelete="CASCADE"),
        nullable=False,
    )
    entry_id = Column(Text, nullable=False)
    manufacturer_designation = Column(Text, nullable=False)
    symbol_descriptor = Column(Text, nullable=True)
    colour = Column(Text, nullable=True)
    state = Column(Text, nullable=True)
    displayed_message = Column(Text, nullable=True)
    audible_signal = Column(Text, nullable=True)
    documented_meaning = Column(Text, nullable=False)
    documented_instruction = Column(Text, nullable=True)
    combined_with_entry_ids = Column(JSONB, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
