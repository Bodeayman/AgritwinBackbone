"""add_planted_at_to_crop_cycles

Revision ID: a1b2c3d4e5f6
Revises: d9e8f7a6b5c4
Create Date: 2026-08-10 18:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'd9e8f7a6b5c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add planted_at column; backfill existing rows with their created_at value
    # so no row is left with NULL, then enforce NOT NULL.
    op.add_column(
        'crop_cycles',
        sa.Column('planted_at', sa.DateTime(), nullable=True),
    )
    # Backfill: use created_at for any existing rows
    op.execute("UPDATE crop_cycles SET planted_at = created_at WHERE planted_at IS NULL")
    # Now enforce NOT NULL
    op.alter_column('crop_cycles', 'planted_at', nullable=False)


def downgrade() -> None:
    op.drop_column('crop_cycles', 'planted_at')
