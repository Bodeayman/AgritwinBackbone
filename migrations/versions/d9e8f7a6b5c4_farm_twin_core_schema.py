"""farm_twin_core_schema

Revision ID: d9e8f7a6b5c4
Revises: 872b066ca791
Create Date: 2026-08-08 22:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import geoalchemy2


revision: str = 'd9e8f7a6b5c4'
down_revision: Union[str, None] = '872b066ca791'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Drop existing tables being restructured
    op.execute("DROP TABLE IF EXISTS crop_mix_allocations CASCADE")
    op.execute("DROP TABLE IF EXISTS crop_mix_recommendations CASCADE")
    op.execute("DROP TABLE IF EXISTS yield_predictions CASCADE")
    op.execute("DROP TABLE IF EXISTS irrigation_plans CASCADE")
    op.execute("DROP TABLE IF EXISTS diagnoses CASCADE")
    op.execute("DROP TABLE IF EXISTS disease_detections CASCADE")
    op.execute("DROP TABLE IF EXISTS satellite_observations CASCADE")
    op.execute("DROP TABLE IF EXISTS satellite_data CASCADE")
    op.execute("DROP TABLE IF EXISTS sensor_readings CASCADE")
    op.execute("DROP TABLE IF EXISTS field_boundaries CASCADE")
    op.execute("DROP TABLE IF EXISTS fields CASCADE")
    op.execute("DROP TABLE IF EXISTS farms CASCADE")
    op.execute("DROP TABLE IF EXISTS ai_models CASCADE")

    # 2. Create ai_models table
    op.create_table(
        'ai_models',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ai_models_name', 'ai_models', ['name'])
    op.create_index('ix_ai_models_version', 'ai_models', ['version'])

    # 3. Recreate farms table with owner_id FK to users
    op.create_table(
        'farms',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_farms_owner_id', 'farms', ['owner_id'])

    # 4. Recreate fields table with crop_type
    op.create_table(
        'fields',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('farm_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('crop_type', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['farm_id'], ['farms.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_fields_farm_id', 'fields', ['farm_id'])

    # 5. Create field_boundaries table (1:1 with fields, storing PostGIS geometry)
    op.create_table(
        'field_boundaries',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('field_id', sa.Integer(), nullable=False),
        sa.Column('boundary', geoalchemy2.types.Geometry(geometry_type='POLYGON', srid=4326, spatial_index=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['field_id'], ['fields.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('field_id')
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_field_boundaries_boundary ON field_boundaries USING gist (boundary)")

    # 6. Recreate sensor_readings table
    op.create_table(
        'sensor_readings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('field_id', sa.Integer(), nullable=False),
        sa.Column('sensor_id', sa.String(length=100), nullable=True),
        sa.Column('soil_moisture', sa.Float(), nullable=True),
        sa.Column('soil_temperature', sa.Float(), nullable=True),
        sa.Column('air_temperature', sa.Float(), nullable=True),
        sa.Column('humidity', sa.Float(), nullable=True),
        sa.Column('soil_ph', sa.Float(), nullable=True),
        sa.Column('electrical_conductivity', sa.Float(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['field_id'], ['fields.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sensor_readings_field_recorded', 'sensor_readings', ['field_id', 'recorded_at'])

    # 7. Create satellite_observations table
    op.create_table(
        'satellite_observations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('field_id', sa.Integer(), nullable=False),
        sa.Column('model_id', sa.Integer(), nullable=True),
        sa.Column('ndvi', sa.Float(), nullable=True),
        sa.Column('ndmi', sa.Float(), nullable=True),
        sa.Column('evi', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='processed'),
        sa.Column('image_reference', sa.String(length=512), nullable=True),
        sa.Column('captured_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['field_id'], ['fields.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['model_id'], ['ai_models.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_satellite_obs_field_captured', 'satellite_observations', ['field_id', 'captured_at'])

    # 8. Create diagnoses table
    op.create_table(
        'diagnoses',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('field_id', sa.Integer(), nullable=False),
        sa.Column('model_id', sa.Integer(), nullable=True),
        sa.Column('image_reference', sa.String(length=512), nullable=True),
        sa.Column('crop_type', sa.String(length=100), nullable=True),
        sa.Column('disease_or_pest', sa.String(length=255), nullable=False),
        sa.Column('severity', sa.Float(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='processed'),
        sa.Column('diagnosed_at', sa.DateTime(), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('treatment_suggestion', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['field_id'], ['fields.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['model_id'], ['ai_models.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_diagnoses_field_diagnosed', 'diagnoses', ['field_id', 'diagnosed_at'])

    # 9. Create irrigation_plans table
    op.create_table(
        'irrigation_plans',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('field_id', sa.Integer(), nullable=False),
        sa.Column('model_id', sa.Integer(), nullable=True),
        sa.Column('water_requirement', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(length=50), nullable=False),
        sa.Column('recommended_date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['field_id'], ['fields.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['model_id'], ['ai_models.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_irrigation_plans_field_date', 'irrigation_plans', ['field_id', 'recommended_date'])

    # 10. Create yield_predictions table
    op.create_table(
        'yield_predictions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('field_id', sa.Integer(), nullable=False),
        sa.Column('model_id', sa.Integer(), nullable=True),
        sa.Column('crop_type', sa.String(length=100), nullable=False),
        sa.Column('predicted_yield', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(length=50), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='processed'),
        sa.Column('prediction_date', sa.Date(), nullable=False),
        sa.Column('model_version', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['field_id'], ['fields.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['model_id'], ['ai_models.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_yield_predictions_field_date', 'yield_predictions', ['field_id', 'prediction_date'])

    # 11. Create crop_mix_recommendations table
    op.create_table(
        'crop_mix_recommendations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('field_id', sa.Integer(), nullable=False),
        sa.Column('model_id', sa.Integer(), nullable=True),
        sa.Column('expected_profit', sa.Float(), nullable=True),
        sa.Column('binding_constraint', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='processed'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['field_id'], ['fields.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['model_id'], ['ai_models.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_crop_mix_recs_field', 'crop_mix_recommendations', ['field_id'])

    # 12. Create crop_mix_allocations table
    op.create_table(
        'crop_mix_allocations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('recommendation_id', sa.Integer(), nullable=False),
        sa.Column('crop_type', sa.String(length=100), nullable=False),
        sa.Column('allocated_area', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(['recommendation_id'], ['crop_mix_recommendations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_crop_mix_allocations_rec_id', 'crop_mix_allocations', ['recommendation_id'])


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS crop_mix_allocations CASCADE")
    op.execute("DROP TABLE IF EXISTS crop_mix_recommendations CASCADE")
    op.execute("DROP TABLE IF EXISTS yield_predictions CASCADE")
    op.execute("DROP TABLE IF EXISTS irrigation_plans CASCADE")
    op.execute("DROP TABLE IF EXISTS diagnoses CASCADE")
    op.execute("DROP TABLE IF EXISTS satellite_observations CASCADE")
    op.execute("DROP TABLE IF EXISTS sensor_readings CASCADE")
    op.execute("DROP TABLE IF EXISTS field_boundaries CASCADE")
    op.execute("DROP TABLE IF EXISTS fields CASCADE")
    op.execute("DROP TABLE IF EXISTS farms CASCADE")
    op.execute("DROP TABLE IF EXISTS ai_models CASCADE")
