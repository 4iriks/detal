"""detail article length

Revision ID: 20260517_0002
Revises: 20260517_0001
Create Date: 2026-05-17 12:10:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260517_0002"
down_revision: Union[str, None] = "20260517_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "details",
        "article",
        existing_type=sa.String(length=80),
        type_=sa.String(length=100),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "details",
        "article",
        existing_type=sa.String(length=100),
        type_=sa.String(length=80),
        existing_nullable=False,
    )
