from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class ExternalReference(Base):
    __tablename__ = "external_references"
    __table_args__ = (
        UniqueConstraint("reference_system", "reference_type", "reference_value", name="external_references_uq"),
        {"schema": "cpl"},
    )

    external_reference_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    entity_type = Column(Text, nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    reference_system = Column(Text, nullable=False)
    reference_type = Column(Text, nullable=False)
    reference_value = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
