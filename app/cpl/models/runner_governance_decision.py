from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base import Base


class RunnerGovernanceDecision(Base):
    """Durable governed record of a material B6 mutation (REQ-B6-076..079,
    061). Implements the frozen pipeline: REQUEST -> AUTHORITY ->
    DECISION -> EFFECT -> HISTORY (WHAT §25) for RunnerExecution/
    RunnerArtifact — a distinct object from B5's CanonicalCaseDecision
    (available precedent, not a copy: B6 needs `decision_mode` to
    distinguish REQ-B6-076's full authority evaluation from REQ-B6-015's
    automatic, rule-bound acceptance of a runner-reported transition,
    which B5 has no analogue for).

    execution_id/artifact_id are both DEFERRABLE INITIALLY DEFERRED
    (mirroring canonical_case_decisions.case_id, R7 pattern): admission
    and registration decisions are recorded before the governed row
    exists; Postgres checks the FK at COMMIT time, by which point the
    row has also been inserted in the same transaction.
    """

    __tablename__ = "runner_governance_decisions"
    __table_args__ = (
        CheckConstraint(
            "decision_type IN ('EXECUTION_ADMISSION', 'EXECUTION_STATUS_TRANSITION', "
            "'ARTIFACT_REGISTRATION', 'ARTIFACT_SUPERSESSION')",
            name="runner_governance_decisions_type_chk",
        ),
        CheckConstraint(
            "decision_mode IN ('AUTHORITY_EVALUATION', 'AUTOMATIC_RULE_BOUND')",
            name="runner_governance_decisions_mode_chk",
        ),
        CheckConstraint("result IN ('EXECUTED', 'REJECTED')", name="runner_governance_decisions_result_chk"),
        CheckConstraint(
            "rejection_category IS NULL OR rejection_category IN "
            "('AUTHORITY_REJECTION', 'SEMANTIC_REJECTION', 'UNRESOLVED', 'CONFLICT')",
            name="runner_governance_decisions_rejection_category_chk",
        ),
        CheckConstraint(
            "(execution_id IS NOT NULL) OR (artifact_id IS NOT NULL)",
            name="runner_governance_decisions_target_chk",
        ),
        {"schema": "cpl"},
    )

    decision_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    decision_type = Column(Text, nullable=False)
    decision_mode = Column(Text, nullable=False)
    execution_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cpl.runner_executions.execution_id", ondelete="RESTRICT", deferrable=True, initially="DEFERRED"),
        nullable=True,
    )
    artifact_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cpl.runner_artifacts.artifact_id", ondelete="RESTRICT", deferrable=True, initially="DEFERRED"),
        nullable=True,
    )
    authority_context = Column(JSONB, nullable=True)
    prior_value = Column(JSONB, nullable=True)
    new_value = Column(JSONB, nullable=True)
    result = Column(Text, nullable=False)
    rejection_category = Column(Text, nullable=True)
    decided_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
