"""add diagnosis detail fields

Revision ID: f1e2d3c4b5a6
Revises: e1f2a3b4c5d6
Create Date: 2026-08-12 08:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1e2d3c4b5a6'
down_revision: Union[str, None] = 'e1f2a3b4c5d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to diagnoses table
    op.add_column('diagnoses', sa.Column('leaf_boundary_box', sa.JSON(), nullable=True))
    op.add_column('diagnoses', sa.Column('detected_diseases', sa.JSON(), nullable=True))
    op.add_column('diagnoses', sa.Column('disease_confidences', sa.JSON(), nullable=True))


def downgrade() -> None:
    # Remove the new columns
    op.drop_column('diagnoses', 'disease_confidences')
    op.drop_column('diagnoses', 'detected_diseases')
    op.drop_column('diagnoses', 'leaf_boundary_box')
