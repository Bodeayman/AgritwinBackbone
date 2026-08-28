"""add npk and pressure fields

Revision ID: fd9af54a4775
Revises: f1e2d3c4b5a6
Create Date: 2026-08-24 13:27:41.888904

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fd9af54a4775'
down_revision: Union[str, None] = 'f1e2d3c4b5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add NPK columns to sensor_readings
    op.add_column('sensor_readings', sa.Column('n_level', sa.Float(), nullable=True))
    op.add_column('sensor_readings', sa.Column('p_level', sa.Float(), nullable=True))
    op.add_column('sensor_readings', sa.Column('k_level', sa.Float(), nullable=True))

    # Replace wind_speed with pressure in weather table
    op.drop_column('weather', 'wind_speed')
    op.add_column('weather', sa.Column('pressure', sa.Float(), nullable=True))


def downgrade() -> None:
    # Remove pressure column from weather and restore wind_speed
    op.drop_column('weather', 'pressure')
    op.add_column('weather', sa.Column('wind_speed', sa.Float(), nullable=True))

    # Drop NPK columns from sensor_readings
    op.drop_column('sensor_readings', 'k_level')
    op.drop_column('sensor_readings', 'p_level')
    op.drop_column('sensor_readings', 'n_level')
