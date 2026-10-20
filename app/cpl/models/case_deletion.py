from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime, Integer, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base import Base


class CaseDeletion(Base):
    """Technical trace of the governed deletion of one expired Case
    (REQ-B5-116, migration 031). One row per deleted Case, never updated.
    It keeps the Case's opaque identifier, the operation, its reason, the
    retention period applied, the opaque operator reference and how many
    rows of each kind were deleted -- never any content of the Case, no
    contact, no vehicle and no vehicle identifier. No foreign key: the Case
    it names no longer exists."""

    __tablename__ = "case_deletions"
    __table_args__ = (
        CheckConstraint("reason = 'RETENTION_POLICY'", name="case_deletions_reason_chk"),
        CheckConstraint("anchor = 'creation_dossier'", name="case_deletions_anchor_chk"),
        CheckConstraint("retention_days >= 1", name="case_deletions_retention_days_chk"),
        {"schema": "cpl"},
    )

    case_id = Column(UUID(as_uuid=True), primary_key=True)
    operation_id = Column(UUID(as_uuid=True), nullable=False)
    reason = Column(Text, nullable=False, default="RETENTION_POLICY")
    retention_days = Column(Integer, nullable=False)
    anchor = Column(Text, nullable=False, default="creation_dossier")
    operator_reference = Column(Text, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    deleted_counts = Column(JSONB, nullable=False)
