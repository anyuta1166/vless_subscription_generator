"""Add custom name to server assignments.

Revision ID: 0002_add_assignment_custom_name
Revises: 0001_baseline
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_add_assignment_custom_name"
down_revision = "0001_baseline"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "server_users",
        sa.Column(
            "custom_name",
            sa.String(length=128),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "server_users",
        "custom_name",
    )
