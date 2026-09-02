"""Create contact_point_verifications (REQ-B3-116..120, 078) and
contact_creation_requests (REQ-B3-067/124/125 idempotency)

Revision ID: 021
Revises: 020
Create Date: 2026-09-02
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "021"
down_revision: Union[str, Sequence[str], None] = "020"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "contact_point_verifications",
        sa.Column("verification_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("contact_point_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("verification_class", sa.Text, nullable=False),
        sa.Column("issuer", sa.Text, nullable=False),
        sa.Column("result", sa.Text, nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("authority_context", postgresql.JSONB, nullable=True),
        sa.Column("replay_key", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("result IN ('ACCEPTED', 'REJECTED')", name="cp_verifications_result_chk"),
        sa.ForeignKeyConstraint(["contact_point_id"], ["cpl.contact_points.contact_point_id"], ondelete="RESTRICT", name="cp_verifications_point_fk"),
        schema="cpl",
    )
    op.create_index("cp_verifications_point_idx", "contact_point_verifications", ["contact_point_id"], schema="cpl")
    op.create_index(
        "cp_verifications_replay_uq",
        "contact_point_verifications",
        ["contact_point_id", "verification_class", "replay_key"],
        unique=True,
        schema="cpl",
        postgresql_where=sa.text("replay_key IS NOT NULL"),
    )

    op.create_table(
        "contact_creation_requests",
        sa.Column("idempotency_key", sa.Text, primary_key=True),
        sa.Column("contact_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["contact_id"], ["cpl.contacts.contact_id"], ondelete="RESTRICT", name="contact_creation_requests_contact_fk"),
        schema="cpl",
    )


def downgrade() -> None:
    op.drop_table("contact_creation_requests", schema="cpl")
    op.drop_index("cp_verifications_replay_uq", table_name="contact_point_verifications", schema="cpl")
    op.drop_index("cp_verifications_point_idx", table_name="contact_point_verifications", schema="cpl")
    op.drop_table("contact_point_verifications", schema="cpl")
