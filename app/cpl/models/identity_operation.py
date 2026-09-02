from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base import Base


class IdentityOperation(Base):
    """Durable provenance record for material B3 identity operations (REQ-B3-121/122/123)."""

    __tablename__ = "identity_operations"
    __table_args__ = (
        CheckConstraint(
            "operation_type IN ("
            "'CREATE_CONTACT','ADD_CONTACT_POINT','VERIFY_CONTACT_POINT',"
            "'INVALIDATE_CONTACT_POINT','SET_PRIMARY_CONTACT_POINT',"
            "'ATTACH_ACCOUNT','DISABLE_ACCOUNT','REVOKE_ACCOUNT',"
            "'DETECT_DUPLICATE_CONTACT','PROPOSE_MERGE','MERGE_CONTACTS')",
            name="identity_operations_type_chk",
        ),
        {"schema": "cpl"},
    )

    operation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    operation_type = Column(Text, nullable=False)
    actor_reference = Column(Text, nullable=True)
    authority_context = Column(JSONB, nullable=True)
    evidence_reference = Column(JSONB, nullable=True)
    affected_object_ids = Column(JSONB, nullable=True)
    decision = Column(Text, nullable=False)
    result = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
