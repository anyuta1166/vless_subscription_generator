"""Initial schema baseline.

Revision ID: 0001_baseline
Revises:
"""

from typing import Sequence, Union


revision: str = "0001_baseline"
down_revision: Union[str, Sequence[str], None] = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
