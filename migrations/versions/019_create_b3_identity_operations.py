"""Create identity_operations — durable provenance for material B3 mutations (REQ-B3-121/122/123)

Revision ID: 019
Revises: 018
Create Date: 2026-09-02
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "019"
down_revision: Union[str, Sequence[str], None] = "018"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "identity_operations",
        sa.Column("operation_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("operation_type", sa.Text, nullable=False),
        sa.Column("actor_reference", sa.Text, nullable=True),
        sa.Column("authority_context", postgresql.JSONB, nullable=True),
        sa.Column("evidence_reference", postgresql.JSONB, nullable=True),
        sa.Column("affected_object_ids", postgresql.JSONB, nullable=True),
        sa.Column("decision", sa.Text, nullable=False),
        sa.Column("result", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint(
            "operation_type IN ("
            "'CREATE_CONTACT','ADD_CONTACT_POINT','VERIFY_CONTACT_POINT',"
            "'INVALIDATE_CONTACT_POINT','SET_PRIMARY_CONTACT_POINT',"
            "'ATTACH_ACCOUNT','DISABLE_ACCOUNT','REVOKE_ACCOUNT',"
            "'DETECT_DUPLICATE_CONTACT','PROPOSE_MERGE','MERGE_CONTACTS')",
            name="identity_operations_type_chk",
        ),
        schema="cpl",
    )
    op.create_index("identity_operations_type_idx", "identity_operations", ["operation_type"], schema="cpl")
    op.create_index("identity_operations_created_idx", "identity_operations", [sa.text("created_at DESC")], schema="cpl")


def downgrade() -> None:
    op.drop_index("identity_operations_created_idx", table_name="identity_operations", schema="cpl")
    op.drop_index("identity_operations_type_idx", table_name="identity_operations", schema="cpl")
    op.drop_table("identity_operations", schema="cpl")
