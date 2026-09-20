"""add disease table

Revision ID: i1j2k3l4m5n6
Revises: h1i2j3k4l5m6
Create Date: 2024-09-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'i1j2k3l4m5n6'
down_revision: Union[str, None] = 'h1i2j3k4l5m6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create diseases table
    op.create_table(
        'diseases',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('external_disease_id', sa.String(100), nullable=True),
        sa.Column('disease_name', sa.String(255), nullable=False),
        sa.Column('crop_type', sa.String(100), nullable=False),
        sa.Column('local_synonyms', postgresql.JSON(), nullable=True),
        sa.Column('pathogen', sa.String(255), nullable=True),
        sa.Column('pathogen_type', sa.String(255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('visual_features_json', postgresql.JSON(), nullable=True),
        sa.Column('evidence_level', sa.String(50), nullable=True),
        sa.Column('source', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_diseases_external_disease_id', 'diseases', ['external_disease_id'])
    op.create_index('ix_diseases_disease_name', 'diseases', ['disease_name'])
    op.create_index('ix_diseases_crop_type', 'diseases', ['crop_type'])
    
    # Add disease_id column to diagnoses table
    op.add_column('diagnoses', sa.Column('disease_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_diagnoses_disease_id', 'diagnoses', 'diseases', ['disease_id'], ['id'], ondelete='SET NULL')
    op.create_index('ix_diagnoses_disease_id', 'diagnoses', ['disease_id'])


def downgrade() -> None:
    # Reverse diagnoses table changes
    op.drop_index('ix_diagnoses_disease_id', table_name='diagnoses')
    op.drop_constraint('fk_diagnoses_disease_id', 'diagnoses')
    op.drop_column('diagnoses', 'disease_id')
    
    # Drop diseases table
    op.drop_index('ix_diseases_crop_type', table_name='diseases')
    op.drop_index('ix_diseases_disease_name', table_name='diseases')
    op.drop_index('ix_diseases_external_disease_id', table_name='diseases')
    op.drop_table('diseases')