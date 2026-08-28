"""fix weather foreign key

Revision ID: e1f2a3b4c5d6
Revises: c3d4e5f6a7d8
Create Date: 2026-08-11 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e1f2a3b4c5d6'
down_revision: Union[str, None] = 'c3d4e5f6a7d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add foreign key constraint for weather table
    op.create_foreign_key(
        'weather_field_id_fkey',
        'weather',
        'fields',
        ['field_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    # Remove foreign key constraint
    op.drop_constraint('weather_field_id_fkey', 'weather', type_='foreignkey')
