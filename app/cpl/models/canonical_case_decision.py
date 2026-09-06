from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base import Base


class CanonicalCaseDecision(Base):
    """Durable governed record of a material B5 Case mutation
    (REQ-B5-046..051). Implements the frozen pipeline invariant:
    REQUEST -> AUTHORITY -> DECISION -> EFFECT -> HISTORY. `prior_value`/
    `new_value` generically capture correction provenance for Case
    metadata, participant records, and CaseEvent corrections without
    requiring per-field supersession columns on those tables."""

    __tablename__ = "canonical_case_decisions"
    __table_args__ = (
        CheckConstraint(
            "decision_type IN ('CREATE', 'STATUS_TRANSITION', 'PARTICIPANT_ADD', "
            "'PARTICIPANT_REMOVE', 'METADATA_CORRECTION', 'EVENT_CORRECTION', "
            "'ASSET_REBIND_ATTEMPT')",
            name="canonical_case_decisions_type_chk",
        ),
        CheckConstraint("result IN ('EXECUTED', 'HOLD', 'REJECTED')", name="canonical_case_decisions_result_chk"),
        CheckConstraint(
            "rejection_category IS NULL OR rejection_category IN "
            "('AUTHORITY_REJECTION', 'SEMANTIC_REJECTION', 'UNRESOLVED', 'CONFLICT')",
            name="canonical_case_decisions_rejection_category_chk",
        ),
        {"schema": "cpl"},
    )

    decision_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cpl.cases.case_id", ondelete="RESTRICT"), nullable=False)
    decision_type = Column(Text, nullable=False)
    authority_context = Column(JSONB, nullable=True)
    prior_value = Column(JSONB, nullable=True)
    new_value = Column(JSONB, nullable=True)
    result = Column(Text, nullable=False)
    rejection_category = Column(Text, nullable=True)
    decided_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    supersedes_decision_id = Column(UUID(as_uuid=True), ForeignKey("cpl.canonical_case_decisions.decision_id", ondelete="RESTRICT"), nullable=True)
