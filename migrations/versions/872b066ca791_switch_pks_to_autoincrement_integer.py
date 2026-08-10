"""switch_pks_to_autoincrement_integer

Revision ID: 872b066ca791
Revises: 2fa598f0d75f
Create Date: 2026-08-08 20:12:20.390806

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import geoalchemy2


# revision identifiers, used by Alembic.
revision: str = '872b066ca791'
down_revision: Union[str, None] = '2fa598f0d75f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Drop existing tables that depend on old PK types (destructive migration as approved by user)
    op.execute("DROP TABLE IF EXISTS crop_cycles CASCADE")
    op.execute("DROP TABLE IF EXISTS disease_detections CASCADE")
    op.execute("DROP TABLE IF EXISTS satellite_data CASCADE")
    op.execute("DROP TABLE IF EXISTS sensor_readings CASCADE")
    op.execute("DROP TABLE IF EXISTS weather CASCADE")
    op.execute("DROP TABLE IF EXISTS fields CASCADE")
    op.execute("DROP TABLE IF EXISTS farms CASCADE")

    # 2. Recreate farms with Integer PK
    op.create_table('farms',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('owner', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. Recreate fields with Integer PK and Integer farm_id FK
    op.create_table('fields',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('farm_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('geom', geoalchemy2.types.Geometry(geometry_type='POLYGON', srid=4326, dimension=2, from_text='ST_GeomFromEWKT', name='geometry', nullable=False), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['farm_id'], ['farms.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_fields_geom ON fields USING gist (geom)")

    # 4. Recreate crop_cycles with Integer PK and Integer field_id FK
    op.create_table('crop_cycles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('field_id', sa.Integer(), nullable=False),
        sa.Column('crop', sa.String(length=100), nullable=False),
        sa.Column('planting_date', sa.Date(), nullable=False),
        sa.Column('expected_harvest_date', sa.Date(), nullable=False),
        sa.Column('actual_harvest_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['field_id'], ['fields.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 5. Recreate disease_detections with Integer PK and Integer field_id FK
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

    # 6. Recreate satellite_data with Integer PK and Integer field_id FK
    op.create_table('satellite_data',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('field_id', sa.Integer(), nullable=False),
        sa.Column('ndvi', sa.Float(), nullable=True),
        sa.Column('ndmi', sa.Float(), nullable=True),
        sa.Column('captured_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['field_id'], ['fields.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 7. Recreate sensor_readings with Integer PK and Integer field_id FK
    op.create_table('sensor_readings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('field_id', sa.Integer(), nullable=False),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.Column('soil_moisture', sa.Float(), nullable=True),
        sa.Column('soil_temperature', sa.Float(), nullable=True),
        sa.Column('air_temperature', sa.Float(), nullable=True),
        sa.Column('humidity', sa.Float(), nullable=True),
        sa.Column('soil_ph', sa.Float(), nullable=True),
        sa.Column('electrical_conductivity', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['field_id'], ['fields.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 8. Recreate weather with Integer PK and Integer field_id FK
    op.create_table('weather',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('field_id', sa.Integer(), nullable=False),
        sa.Column('temperature', sa.Float(), nullable=True),
        sa.Column('humidity', sa.Float(), nullable=True),
        sa.Column('rainfall', sa.Float(), nullable=True),
        sa.Column('forecast_rain', sa.Float(), nullable=True),
        sa.Column('wind_speed', sa.Float(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['field_id'], ['fields.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Drop all integer-based tables
    op.execute("DROP TABLE IF EXISTS crop_cycles CASCADE")
    op.execute("DROP TABLE IF EXISTS disease_detections CASCADE")
    op.execute("DROP TABLE IF EXISTS satellite_data CASCADE")
    op.execute("DROP TABLE IF EXISTS sensor_readings CASCADE")
    op.execute("DROP TABLE IF EXISTS weather CASCADE")
    op.execute("DROP TABLE IF EXISTS fields CASCADE")
    op.execute("DROP TABLE IF EXISTS farms CASCADE")

    # Recreate the original varchar-based tables
    op.create_table('farms',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('owner', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('fields',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('farm_id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('geom', geoalchemy2.types.Geometry(geometry_type='POLYGON', srid=4326, dimension=2, from_text='ST_GeomFromEWKT', name='geometry', nullable=False), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['farm_id'], ['farms.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_fields_geom ON fields USING gist (geom)")

    op.create_table('crop_cycles',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('field_id', sa.String(length=50), nullable=False),
        sa.Column('crop', sa.String(length=100), nullable=False),
        sa.Column('planting_date', sa.Date(), nullable=False),
        sa.Column('expected_harvest_date', sa.Date(), nullable=False),
        sa.Column('actual_harvest_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['field_id'], ['fields.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('disease_detections',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('field_id', sa.String(length=50), nullable=False),
        sa.Column('image_url', sa.String(), nullable=False),
        sa.Column('disease_name', sa.String(), nullable=False),
        sa.Column('severity', sa.Float(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['field_id'], ['fields.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('satellite_data',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('field_id', sa.String(length=50), nullable=False),
        sa.Column('ndvi', sa.Float(), nullable=True),
        sa.Column('ndmi', sa.Float(), nullable=True),
        sa.Column('captured_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['field_id'], ['fields.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('sensor_readings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('field_id', sa.String(length=50), nullable=False),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.Column('soil_moisture', sa.Float(), nullable=True),
        sa.Column('soil_temperature', sa.Float(), nullable=True),
        sa.Column('air_temperature', sa.Float(), nullable=True),
        sa.Column('humidity', sa.Float(), nullable=True),
        sa.Column('soil_ph', sa.Float(), nullable=True),
        sa.Column('electrical_conductivity', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['field_id'], ['fields.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('weather',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('field_id', sa.String(length=50), nullable=False),
        sa.Column('temperature', sa.Float(), nullable=True),
        sa.Column('humidity', sa.Float(), nullable=True),
        sa.Column('rainfall', sa.Float(), nullable=True),
        sa.Column('forecast_rain', sa.Float(), nullable=True),
        sa.Column('wind_speed', sa.Float(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['field_id'], ['fields.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
