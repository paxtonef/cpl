"""Consolidation migration — indexes already applied per-table

Revision ID: 018
Revises: 017
Create Date: 2026-08-28
"""
from typing import Sequence, Union
from alembic import op

revision: str = "018"
down_revision: Union[str, Sequence[str], None] = "017"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
