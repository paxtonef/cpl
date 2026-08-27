"""Bootstrap: create schemas and extensions

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute("CREATE SCHEMA IF NOT EXISTS cpl")
    op.execute("CREATE SCHEMA IF NOT EXISTS automotive")


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS automotive CASCADE")
    op.execute("DROP SCHEMA IF EXISTS cpl CASCADE")
    op.execute("DROP EXTENSION IF NOT EXISTS pgcrypto")
