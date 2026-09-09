from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from app.db.base import Base


class RunnerArtifactSchemaDefinition(Base):
    """Registry of (schema_name, schema_version) -> minimal structural
    contract (REQ-B6-089). Deliberately minimal — a required-field list
    plus a type map, not a general JSON Schema engine — per the frozen
    exclusion of a generic Evidence ontology / Artifact platform
    (WHAT §5, REQ-B6-083). `RunnerArtifact.artifact_status` can only
    reach VALIDATED (REQ-B6-032) when its declared (schema_name,
    schema_version) pair resolves to a row here and the payload
    conforms; an unregistered pair routes the artifact to REJECTED
    (REQ-B6-033, structural reason)."""

    __tablename__ = "runner_artifact_schema_definitions"
    __table_args__ = {"schema": "cpl"}

    schema_name = Column(Text, primary_key=True)
    schema_version = Column(Text, primary_key=True)
    required_fields = Column(JSONB, nullable=False)
    field_types = Column(JSONB, nullable=False)
    registered_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
