"""Create vehicle_details table

Revision ID: 008
Revises: 007
Create Date: 2026-08-28
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "008"
down_revision: Union[str, Sequence[str], None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "vehicle_details",
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("vin_display", sa.Text, nullable=True),
        sa.Column("registration_display", sa.Text, nullable=True),
        sa.Column("registration_country", sa.Text, nullable=True),
        sa.Column("make", sa.Text, nullable=True),
        sa.Column("model", sa.Text, nullable=True),
        sa.Column("variant", sa.Text, nullable=True),
        sa.Column("first_registration_date", sa.Date, nullable=True),
        sa.Column("source_resolution_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["asset_id"], ["cpl.assets.asset_id"], ondelete="RESTRICT", name="vehicle_details_asset_fk"),
        schema="automotive",
    )


def downgrade() -> None:
    op.drop_table("vehicle_details", schema="automotive")
