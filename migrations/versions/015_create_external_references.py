"""Create external_references table

Revision ID: 015
Revises: 014
Create Date: 2026-08-28
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "015"
down_revision: Union[str, Sequence[str], None] = "014"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "external_references",
        sa.Column("external_reference_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("entity_type", sa.Text, nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reference_system", sa.Text, nullable=False),
        sa.Column("reference_type", sa.Text, nullable=False),
        sa.Column("reference_value", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("reference_system", "reference_type", "reference_value", name="external_references_uq"),
        schema="cpl",
    )
    op.create_index("external_references_entity_idx", "external_references", ["entity_type", "entity_id"], schema="cpl")


def downgrade() -> None:
    op.drop_index("external_references_entity_idx", table_name="external_references", schema="cpl")
    op.drop_table("external_references", schema="cpl")
