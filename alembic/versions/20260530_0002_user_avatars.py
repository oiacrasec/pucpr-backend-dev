"""user avatars

Revision ID: 20260530_0002
Revises: 20260506_0001
Create Date: 2026-05-30 12:20:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260530_0002"
down_revision = "20260506_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_avatars",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("storage_backend", sa.String(length=20), nullable=False),
        sa.Column("object_key", sa.String(length=512), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", name="uq_user_avatars_user_id"),
    )


def downgrade() -> None:
    op.drop_table("user_avatars")
