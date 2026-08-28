"""data model refactoring

Revision ID: c3d4e5f6a7d8
Revises: b2c3d4e5f6a7
Create Date: 2026-08-11 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import geoalchemy2


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7d8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add foreign key constraints for satellite_observations (tables already exist)
    op.add_column('satellite_observations', sa.Column('satellite_id', sa.Integer(), nullable=True))
    op.add_column('satellite_observations', sa.Column('imagery_id', sa.Integer(), nullable=True))
    op.add_column('satellite_observations', sa.Column('observation_type', sa.String(length=50), nullable=False, server_default='processed'))
    op.add_column('satellite_observations', sa.Column('cloud_cover_pct', sa.Float(), nullable=True))
    op.add_column('satellite_observations', sa.Column('additional_metadata', sa.JSON(), nullable=True))
    
    # Drop old column if exists
    try:
        op.drop_column('satellite_observations', 'image_reference')
    except:
        pass
    
    # Create foreign key constraints
    op.create_foreign_key('fk_satellite_observations_satellite_id', 'satellite_observations', 'satellites', ['satellite_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('fk_satellite_observations_imagery_id', 'satellite_observations', 'imagery', ['imagery_id'], ['id'], ondelete='SET NULL')
    op.create_index('ix_satellite_obs_satellite_captured', 'satellite_observations', ['satellite_id', 'captured_at'], unique=False)
    
    # Drop old index if exists
    try:
        op.drop_index('ix_satellite_obs_field_captured', 'satellite_observations')
    except:
        pass

    # Update Diagnosis table
    op.add_column('diagnoses', sa.Column('imagery_id', sa.Integer(), nullable=True))
    try:
        op.drop_column('diagnoses', 'image_reference')
    except:
        pass
    op.create_foreign_key('fk_diagnoses_imagery_id', 'diagnoses', 'imagery', ['imagery_id'], ['id'], ondelete='SET NULL')

    # Update YieldPrediction table
    try:
        op.drop_column('yield_predictions', 'model_version')
    except:
        pass

    # Update Field table
    try:
        op.drop_column('fields', 'crop_type')
    except:
        pass

    # Update CropCycle table
    op.add_column('crop_cycles', sa.Column('variety', sa.String(length=100), nullable=True))
    op.create_index('ix_crop_cycles_field_status', 'crop_cycles', ['field_id', 'status'], unique=False)

    # Drop deprecated tables
    op.drop_table('disease_detections', if_exists=True)
    op.drop_table('satellite_data', if_exists=True)


def downgrade() -> None:
    # Reverse all changes
    op.create_table('satellite_data',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('field_id', sa.Integer(), nullable=False),
        sa.Column('ndvi', sa.Float(), nullable=True),
        sa.Column('ndmi', sa.Float(), nullable=True),
        sa.Column('captured_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['field_id'], ['fields.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('disease_detections',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('field_id', sa.Integer(), nullable=False),
        sa.Column('image_url', sa.String(), nullable=False),
        sa.Column('disease_name', sa.String(), nullable=False),
        sa.Column('severity', sa.Float(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['field_id'], ['fields.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.drop_index('ix_crop_cycles_field_status', 'crop_cycles')
    op.drop_column('crop_cycles', 'variety')

    op.add_column('fields', sa.Column('crop_type', sa.String(length=100), nullable=True))

    op.add_column('yield_predictions', sa.Column('model_version', sa.String(length=50), nullable=True))

    op.drop_constraint('fk_diagnoses_imagery_id', 'diagnoses', type_='foreignkey')
    op.add_column('diagnoses', sa.Column('image_reference', sa.String(length=512), nullable=True))
    op.drop_column('diagnoses', 'imagery_id')

    op.drop_index('ix_satellite_obs_satellite_captured', 'satellite_observations')
    op.drop_constraint('fk_satellite_observations_imagery_id', 'satellite_observations', type_='foreignkey')
    op.drop_constraint('fk_satellite_observations_satellite_id', 'satellite_observations', type_='foreignkey')
    op.add_column('satellite_observations', sa.Column('image_reference', sa.String(length=512), nullable=True))
    op.drop_column('satellite_observations', 'additional_metadata')
    op.drop_column('satellite_observations', 'cloud_cover_pct')
    op.drop_column('satellite_observations', 'observation_type')
    op.drop_column('satellite_observations', 'imagery_id')
    op.drop_column('satellite_observations', 'satellite_id')
