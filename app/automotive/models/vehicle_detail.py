from datetime import datetime, timezone
from sqlalchemy import Column, Text, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class VehicleDetail(Base):
    __tablename__ = "vehicle_details"
    __table_args__ = {"schema": "automotive"}

    asset_id = Column(UUID(as_uuid=True), ForeignKey("cpl.assets.asset_id", ondelete="RESTRICT"), primary_key=True)
    vin_display = Column(Text, nullable=True)
    registration_display = Column(Text, nullable=True)
    registration_country = Column(Text, nullable=True)
    make = Column(Text, nullable=True)
    model = Column(Text, nullable=True)
    variant = Column(Text, nullable=True)
    first_registration_date = Column(Date, nullable=True)
    source_resolution_id = Column(UUID(as_uuid=True), ForeignKey("cpl.asset_identity_resolutions.resolution_id", ondelete="RESTRICT"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
