from sqlalchemy import Column, Text, CheckConstraint
from app.db.base import Base


class CaseEventType(Base):
    """Definition-time semantic classification registry for governed
    CaseEvent.event_type values (REQ-B5-035..038, 115, GAP-02). Keeps
    the frozen distinction WORLD EVENT != DOMAIN ASSERTION !=
    CPL OPERATIONAL FACT != CANONICAL DECISION CONSEQUENCE
    determinable at definition time without a per-event-row column
    or a generic Event ontology, and without mandating any specific
    storage mechanism beyond this minimal registry."""

    __tablename__ = "case_event_types"
    __table_args__ = (
        CheckConstraint(
            "semantic_class IN ('CPL_OPERATIONAL_FACT', 'DOMAIN_ASSERTION', "
            "'CANONICAL_DECISION_CONSEQUENCE', 'TECHNICAL_SYSTEM_EVENT')",
            name="case_event_types_semantic_class_chk",
        ),
        {"schema": "cpl"},
    )

    event_type = Column(Text, primary_key=True)
    semantic_class = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
