"""Add record_version columns

Revision ID: 017
Revises: 016
Create Date: 2026-08-28
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "017"
down_revision: Union[str, Sequence[str], None] = "016"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("contacts", sa.Column("record_version", sa.BigInteger, nullable=False, server_default="0"), schema="cpl")
    op.add_column("assets", sa.Column("record_version", sa.BigInteger, nullable=False, server_default="0"), schema="cpl")
    op.add_column("contact_asset_relationships", sa.Column("record_version", sa.BigInteger, nullable=False, server_default="0"), schema="cpl")
    op.add_column("cases", sa.Column("record_version", sa.BigInteger, nullable=False, server_default="0"), schema="cpl")


def downgrade() -> None:
    op.drop_column("cases", "record_version", schema="cpl")
    op.drop_column("contact_asset_relationships", "record_version", schema="cpl")
    op.drop_column("assets", "record_version", schema="cpl")
    op.drop_column("contacts", "record_version", schema="cpl")
