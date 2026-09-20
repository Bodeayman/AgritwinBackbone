"""add input_data_snapshot to yield predictions

Revision ID: g1h2i3j4k5l6
Revises: fd9af54a4775
Create Date: 2024-01-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'g1h2i3j4k5l6'
down_revision: Union[str, None] = 'fd9af54a4775'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add crop_cycle_id column to yield_predictions
    op.add_column('yield_predictions', sa.Column('crop_cycle_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_yield_predictions_crop_cycle_id', 'yield_predictions', 'crop_cycles', ['crop_cycle_id'], ['id'], ondelete='SET NULL')
    
    # Add input_timestamp column to yield_predictions
    op.add_column('yield_predictions', sa.Column('input_timestamp', sa.DateTime(), nullable=False))
    
    # Add input_data_snapshot column to yield_predictions
    op.add_column('yield_predictions', sa.Column('input_data_snapshot', postgresql.JSONB(), nullable=True))
    
    # Create index for crop_cycle and prediction_date
    op.create_index('ix_yield_predictions_crop_cycle_date', 'yield_predictions', ['crop_cycle_id', 'prediction_date'])


def downgrade() -> None:
    # Remove index
    op.drop_index('ix_yield_predictions_crop_cycle_date', table_name='yield_predictions')
    
    # Remove columns
    op.drop_column('yield_predictions', 'input_data_snapshot')
    op.drop_column('yield_predictions', 'input_timestamp')
    op.drop_constraint('fk_yield_predictions_crop_cycle_id', 'yield_predictions', type_='foreignkey')
    op.drop_column('yield_predictions', 'crop_cycle_id')