"""B2-K KNOWLEDGE PERSISTENCE IMPLEMENTATION MANDATE v1, §14. One row per
manufacturer document generation -- see migration 028 for the full
rationale (non-execution-scoped, supersession, idempotency via
content_hash)."""
from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class ManufacturerKnowledgeDocument(Base):
    __tablename__ = "manufacturer_knowledge_documents"
    __table_args__ = (
        CheckConstraint("lifecycle_status IN ('ACTIVE', 'SUPERSEDED')", name="mfr_knowledge_documents_lifecycle_chk"),
        CheckConstraint(
            "source_authority IN ('manufacturer_official', 'unverified_placeholder')",
            name="mfr_knowledge_documents_source_authority_chk",
        ),
        CheckConstraint(
            "supersedes_document_row_id IS NULL OR supersedes_document_row_id <> document_row_id",
            name="mfr_knowledge_documents_not_self_superseded_chk",
        ),
        {"schema": "cpl"},
    )

    document_row_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    manufacturer = Column(Text, nullable=False)
    document_id = Column(Text, nullable=False)
    document_title = Column(Text, nullable=False)
    edition = Column(Text, nullable=True)
    applicability_manufacturer = Column(Text, nullable=False)
    applicability_model = Column(Text, nullable=False)
    applicability_generation = Column(Text, nullable=False)
    applicability_period_start = Column(Text, nullable=True)
    applicability_period_end = Column(Text, nullable=True)
    applicability_period_note = Column(Text, nullable=True)
    source_authority = Column(Text, nullable=False)
    source_locator = Column(Text, nullable=False)
    lifecycle_status = Column(Text, nullable=False, default="ACTIVE")
    verified_at = Column(DateTime(timezone=True), nullable=True)
    supersedes_document_row_id = Column(
        UUID(as_uuid=True), ForeignKey("cpl.manufacturer_knowledge_documents.document_row_id", ondelete="RESTRICT"),
        nullable=True,
    )
    content_hash = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
