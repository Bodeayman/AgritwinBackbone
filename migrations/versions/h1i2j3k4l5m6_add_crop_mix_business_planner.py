"""add crop mix business planner

Revision ID: h1i2j3k4l5m6
Revises: g1h2i3j4k5l6
Create Date: 2024-09-07 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'h1i2j3k4l5m6'
down_revision: Union[str, None] = 'g1h2i3j4k5l6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add columns to farms table (nullable first, then update existing rows)
    op.add_column('farms', sa.Column('zone', sa.String(100), nullable=True))
    op.add_column('farms', sa.Column('total_area_feddans', sa.Float(), nullable=True))
    op.add_column('farms', sa.Column('water_budget_m3', sa.Float(), nullable=True))
    op.add_column('farms', sa.Column('labor_budget_hours', sa.Float(), nullable=True))
    op.add_column('farms', sa.Column('fertilizer_budget_kg', sa.Float(), nullable=True))
    op.add_column('farms', sa.Column('labor_rate_egp_per_hour', sa.Float(), nullable=True))
    op.add_column('farms', sa.Column('fertilizer_rate_egp_per_kg', sa.Float(), nullable=True))
    
    # Update existing rows with default values
    op.execute("UPDATE farms SET zone = 'Delta' WHERE zone IS NULL")
    op.execute("UPDATE farms SET total_area_feddans = 100.0 WHERE total_area_feddans IS NULL")
    op.execute("UPDATE farms SET water_budget_m3 = 500000.0 WHERE water_budget_m3 IS NULL")
    op.execute("UPDATE farms SET labor_budget_hours = 2500.0 WHERE labor_budget_hours IS NULL")
    op.execute("UPDATE farms SET fertilizer_budget_kg = 15000.0 WHERE fertilizer_budget_kg IS NULL")
    op.execute("UPDATE farms SET labor_rate_egp_per_hour = 20.0 WHERE labor_rate_egp_per_hour IS NULL")
    op.execute("UPDATE farms SET fertilizer_rate_egp_per_kg = 1.50 WHERE fertilizer_rate_egp_per_kg IS NULL")
    
    # Make columns NOT NULL
    op.alter_column('farms', 'zone', nullable=False)
    op.alter_column('farms', 'total_area_feddans', nullable=False)
    op.alter_column('farms', 'water_budget_m3', nullable=False)
    op.alter_column('farms', 'labor_budget_hours', nullable=False)
    op.alter_column('farms', 'fertilizer_budget_kg', nullable=False)
    op.alter_column('farms', 'labor_rate_egp_per_hour', nullable=False)
    op.alter_column('farms', 'fertilizer_rate_egp_per_kg', nullable=False)
    
    # Add check constraints for farms
    op.execute("ALTER TABLE farms ADD CONSTRAINT check_farm_zone CHECK (zone IN ('Delta', 'Middle Egypt', 'Upper Egypt', 'Sinai / Reclaimed Lands'))")
    op.execute("ALTER TABLE farms ADD CONSTRAINT check_farm_area_positive CHECK (total_area_feddans > 0)")
    op.execute("ALTER TABLE farms ADD CONSTRAINT check_water_budget_non_negative CHECK (water_budget_m3 >= 0)")
    op.execute("ALTER TABLE farms ADD CONSTRAINT check_labor_budget_non_negative CHECK (labor_budget_hours >= 0)")
    op.execute("ALTER TABLE farms ADD CONSTRAINT check_fertilizer_budget_non_negative CHECK (fertilizer_budget_kg >= 0)")

    # Add columns to fields table (nullable first, then update existing rows)
    op.add_column('fields', sa.Column('name_en', sa.String(255), nullable=True))
    op.add_column('fields', sa.Column('name_ar', sa.String(255), nullable=True))
    op.add_column('fields', sa.Column('area_feddans', sa.Float(), nullable=True))
    op.add_column('fields', sa.Column('soil_ph', sa.Float(), nullable=True))
    op.add_column('fields', sa.Column('soil_ec_ds_m', sa.Float(), nullable=True))
    op.add_column('fields', sa.Column('soil_texture', sa.String(50), nullable=True))
    op.add_column('fields', sa.Column('organic_matter_pct', sa.Float(), nullable=True))
    op.add_column('fields', sa.Column('previous_crop_name', sa.String(100), nullable=True))
    
    # Update existing rows with default values
    op.execute("UPDATE fields SET soil_ph = 6.5 WHERE soil_ph IS NULL")
    op.execute("UPDATE fields SET soil_ec_ds_m = 1.0 WHERE soil_ec_ds_m IS NULL")
    op.execute("UPDATE fields SET soil_texture = 'Loam' WHERE soil_texture IS NULL")
    op.execute("UPDATE fields SET organic_matter_pct = 2.0 WHERE organic_matter_pct IS NULL")
    
    # Add check constraints for fields
    op.execute("ALTER TABLE fields ADD CONSTRAINT check_field_ph_range CHECK (soil_ph BETWEEN 0 AND 14)")
    op.execute("ALTER TABLE fields ADD CONSTRAINT check_field_ec_non_negative CHECK (soil_ec_ds_m >= 0)")
    op.execute("ALTER TABLE fields ADD CONSTRAINT check_field_soil_texture CHECK (soil_texture IN ('Loam', 'Clay', 'Silt', 'Sandy', 'Sandy Loam'))")
    op.execute("ALTER TABLE fields ADD CONSTRAINT check_field_organic_matter_non_negative CHECK (organic_matter_pct >= 0)")
    op.execute("ALTER TABLE fields ADD CONSTRAINT check_field_area_positive CHECK (area_feddans > 0)")

    # Create crop_catalog table
    op.create_table(
        'crop_catalog',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('farm_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['farm_id'], ['farms.id'], ondelete='CASCADE'),
        sa.Column('name_en', sa.String(100), nullable=False),
        sa.Column('name_ar', sa.String(100), nullable=False),
        sa.Column('category', sa.String(50), nullable=False, server_default='General'),
        sa.Column('expected_yield_tons_per_feddan', sa.Float(), nullable=False),
        sa.Column('price_egp_per_ton', sa.Float(), nullable=False),
        sa.Column('production_cost_egp_per_feddan', sa.Float(), nullable=False),
        sa.Column('water_requirement_m3_per_feddan', sa.Float(), nullable=False),
        sa.Column('labor_requirement_hours_per_feddan', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('fertilizer_requirement_kg_per_feddan', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('min_ph', sa.Float(), nullable=False, server_default='4.5'),
        sa.Column('max_ph', sa.Float(), nullable=False, server_default='8.5'),
        sa.Column('max_ec_ds_m', sa.Float(), nullable=False, server_default='3.5'),
        sa.Column('suitable_textures', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('is_perennial', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('expected_yield_tons_per_feddan > 0', name='check_crop_yield_positive'),
        sa.CheckConstraint('price_egp_per_ton >= 0', name='check_crop_price_non_negative'),
        sa.CheckConstraint('production_cost_egp_per_feddan >= 0', name='check_crop_cost_non_negative'),
        sa.CheckConstraint('water_requirement_m3_per_feddan >= 0', name='check_crop_water_non_negative'),
        sa.CheckConstraint('labor_requirement_hours_per_feddan >= 0', name='check_crop_labor_non_negative'),
        sa.CheckConstraint('fertilizer_requirement_kg_per_feddan >= 0', name='check_crop_fertilizer_non_negative'),
        sa.CheckConstraint('min_ph BETWEEN 0 AND 14', name='check_crop_min_ph_range'),
        sa.CheckConstraint('max_ph BETWEEN 0 AND 14', name='check_crop_max_ph_range'),
        sa.CheckConstraint('max_ec_ds_m >= 0', name='check_crop_max_ec_non_negative'),
        sa.CheckConstraint("category IN ('Cereal', 'Vegetable', 'Legume', 'Fruit', 'Oilseed', 'Fiber', 'Forage', 'General')", name='check_crop_category'),
    )
    op.create_index('ix_crop_catalog_farm_id', 'crop_catalog', ['farm_id'])
    
    # Set default array value for suitable_textures
    op.execute("UPDATE crop_catalog SET suitable_textures = ARRAY['Loam', 'Clay', 'Silt', 'Sandy', 'Sandy Loam'] WHERE suitable_textures IS NULL")
    op.alter_column('crop_catalog', 'suitable_textures', nullable=False)

    # Create crop_rotation_matrix table
    op.create_table(
        'crop_rotation_matrix',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('previous_crop_name', sa.String(100), nullable=False),
        sa.Column('candidate_crop_name', sa.String(100), nullable=False),
        sa.Column('suitability_score', sa.Integer(), nullable=False),
        sa.Column('agronomic_notes', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('suitability_score IN (0, 1)', name='check_rotation_score_binary'),
        sa.UniqueConstraint('previous_crop_name', 'candidate_crop_name', name='unique_rotation_pair'),
    )

    # Modify crop_mix_recommendations table (nullable first, then update existing rows)
    op.add_column('crop_mix_recommendations', sa.Column('farm_id', sa.Integer(), nullable=True))
    op.add_column('crop_mix_recommendations', sa.Column('season', sa.String(50), nullable=True))
    op.add_column('crop_mix_recommendations', sa.Column('optimizer_version', sa.String(20), nullable=True))
    op.add_column('crop_mix_recommendations', sa.Column('is_feasible', sa.Boolean(), nullable=True))
    op.add_column('crop_mix_recommendations', sa.Column('total_land_used_feddans', sa.Float(), nullable=True))
    op.add_column('crop_mix_recommendations', sa.Column('total_water_used_m3', sa.Float(), nullable=True))
    op.add_column('crop_mix_recommendations', sa.Column('total_labor_used_hours', sa.Float(), nullable=True))
    op.add_column('crop_mix_recommendations', sa.Column('total_fertilizer_used_kg', sa.Float(), nullable=True))
    op.add_column('crop_mix_recommendations', sa.Column('total_expected_revenue_egp', sa.Float(), nullable=True))
    op.add_column('crop_mix_recommendations', sa.Column('total_production_cost_egp', sa.Float(), nullable=True))
    op.add_column('crop_mix_recommendations', sa.Column('total_labor_cost_egp', sa.Float(), nullable=True))
    op.add_column('crop_mix_recommendations', sa.Column('total_fertilizer_cost_egp', sa.Float(), nullable=True))
    op.add_column('crop_mix_recommendations', sa.Column('net_profit_egp', sa.Float(), nullable=True))
    op.add_column('crop_mix_recommendations', sa.Column('binding_constraints', postgresql.JSONB(), nullable=True))
    op.add_column('crop_mix_recommendations', sa.Column('ai_synthesis_explanation', sa.String(1000), nullable=True))
    
    # Update existing rows with default values
    op.execute("UPDATE crop_mix_recommendations SET season = 'Winter' WHERE season IS NULL")
    op.execute("UPDATE crop_mix_recommendations SET optimizer_version = 'v4' WHERE optimizer_version IS NULL")
    op.execute("UPDATE crop_mix_recommendations SET is_feasible = true WHERE is_feasible IS NULL")
    op.execute("UPDATE crop_mix_recommendations SET total_land_used_feddans = 0.0 WHERE total_land_used_feddans IS NULL")
    op.execute("UPDATE crop_mix_recommendations SET total_water_used_m3 = 0.0 WHERE total_water_used_m3 IS NULL")
    op.execute("UPDATE crop_mix_recommendations SET total_labor_used_hours = 0.0 WHERE total_labor_used_hours IS NULL")
    op.execute("UPDATE crop_mix_recommendations SET total_fertilizer_used_kg = 0.0 WHERE total_fertilizer_used_kg IS NULL")
    op.execute("UPDATE crop_mix_recommendations SET total_expected_revenue_egp = 0.0 WHERE total_expected_revenue_egp IS NULL")
    op.execute("UPDATE crop_mix_recommendations SET total_production_cost_egp = 0.0 WHERE total_production_cost_egp IS NULL")
    op.execute("UPDATE crop_mix_recommendations SET total_labor_cost_egp = 0.0 WHERE total_labor_cost_egp IS NULL")
    op.execute("UPDATE crop_mix_recommendations SET total_fertilizer_cost_egp = 0.0 WHERE total_fertilizer_cost_egp IS NULL")
    op.execute("UPDATE crop_mix_recommendations SET net_profit_egp = 0.0 WHERE net_profit_egp IS NULL")
    
    # For existing records, derive farm_id from field_id
    op.execute("UPDATE crop_mix_recommendations r SET farm_id = (SELECT farm_id FROM fields f WHERE f.id = r.field_id) WHERE farm_id IS NULL")
    
    # Make columns NOT NULL
    op.alter_column('crop_mix_recommendations', 'farm_id', nullable=False)
    op.alter_column('crop_mix_recommendations', 'season', nullable=False)
    op.alter_column('crop_mix_recommendations', 'optimizer_version', nullable=False)
    op.alter_column('crop_mix_recommendations', 'is_feasible', nullable=False)
    op.alter_column('crop_mix_recommendations', 'total_land_used_feddans', nullable=False)
    op.alter_column('crop_mix_recommendations', 'total_water_used_m3', nullable=False)
    op.alter_column('crop_mix_recommendations', 'total_labor_used_hours', nullable=False)
    op.alter_column('crop_mix_recommendations', 'total_fertilizer_used_kg', nullable=False)
    op.alter_column('crop_mix_recommendations', 'total_expected_revenue_egp', nullable=False)
    op.alter_column('crop_mix_recommendations', 'total_production_cost_egp', nullable=False)
    op.alter_column('crop_mix_recommendations', 'total_labor_cost_egp', nullable=False)
    op.alter_column('crop_mix_recommendations', 'total_fertilizer_cost_egp', nullable=False)
    op.alter_column('crop_mix_recommendations', 'net_profit_egp', nullable=False)
    
    # Add foreign key for farm_id
    op.create_foreign_key('fk_crop_mix_recs_farm_id', 'crop_mix_recommendations', 'farms', ['farm_id'], ['id'], ondelete='CASCADE')
    
    # Add check constraints
    op.execute("ALTER TABLE crop_mix_recommendations ADD CONSTRAINT check_rec_season CHECK (season IN ('Winter', 'Summer', 'Nili', 'Perennial'))")
    op.execute("ALTER TABLE crop_mix_recommendations ADD CONSTRAINT check_rec_land_non_negative CHECK (total_land_used_feddans >= 0)")
    op.execute("ALTER TABLE crop_mix_recommendations ADD CONSTRAINT check_rec_water_non_negative CHECK (total_water_used_m3 >= 0)")
    op.execute("ALTER TABLE crop_mix_recommendations ADD CONSTRAINT check_rec_labor_non_negative CHECK (total_labor_used_hours >= 0)")
    op.execute("ALTER TABLE crop_mix_recommendations ADD CONSTRAINT check_rec_fertilizer_non_negative CHECK (total_fertilizer_used_kg >= 0)")
    
    # Create index for farm_id
    op.create_index('ix_crop_mix_recs_farm', 'crop_mix_recommendations', ['farm_id'])
    op.create_index('ix_crop_mix_recs_season', 'crop_mix_recommendations', ['season'])

    # Modify crop_mix_allocations table (nullable first, then update existing rows)
    op.add_column('crop_mix_allocations', sa.Column('field_id', sa.Integer(), nullable=True))
    op.add_column('crop_mix_allocations', sa.Column('crop_id', sa.Integer(), nullable=True))
    op.add_column('crop_mix_allocations', sa.Column('allocated_area_feddans', sa.Float(), nullable=True))
    op.add_column('crop_mix_allocations', sa.Column('expected_profit_contribution_egp', sa.Float(), nullable=True))
    
    # For existing records, derive field_id from recommendation's field_id
    op.execute("UPDATE crop_mix_allocations a SET field_id = (SELECT field_id FROM crop_mix_recommendations r WHERE r.id = a.recommendation_id) WHERE field_id IS NULL")
    
    # Set default values for new numeric columns
    op.execute("UPDATE crop_mix_allocations SET allocated_area_feddans = allocated_area WHERE allocated_area_feddans IS NULL")
    op.execute("UPDATE crop_mix_allocations SET expected_profit_contribution_egp = 0.0 WHERE expected_profit_contribution_egp IS NULL")
    
    # Make columns NOT NULL (except crop_id, which requires a crop catalog reference)
    op.alter_column('crop_mix_allocations', 'field_id', nullable=False)
    op.alter_column('crop_mix_allocations', 'allocated_area_feddans', nullable=False)
    op.alter_column('crop_mix_allocations', 'expected_profit_contribution_egp', nullable=False)
    
    # Add foreign keys (crop_id can be NULL for legacy records)
    op.create_foreign_key('fk_crop_alloc_field_id', 'crop_mix_allocations', 'fields', ['field_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_crop_alloc_crop_id', 'crop_mix_allocations', 'crop_catalog', ['crop_id'], ['id'], ondelete='CASCADE')
    
    # Add check constraint (area must be non-negative)
    op.execute("ALTER TABLE crop_mix_allocations ADD CONSTRAINT check_allocation_area_non_negative CHECK (allocated_area_feddans >= 0)")


def downgrade() -> None:
    # Reverse crop_mix_allocations changes
    op.drop_constraint('check_allocation_area_non_negative', 'crop_mix_allocations')
    op.drop_constraint('fk_crop_alloc_crop_id', 'crop_mix_allocations')
    op.drop_constraint('fk_crop_alloc_field_id', 'crop_mix_allocations')
    op.drop_column('crop_mix_allocations', 'expected_profit_contribution_egp')
    op.drop_column('crop_mix_allocations', 'allocated_area_feddans')
    op.drop_column('crop_mix_allocations', 'crop_id')
    op.drop_column('crop_mix_allocations', 'field_id')

    # Reverse crop_mix_recommendations changes
    op.drop_index('ix_crop_mix_recs_season', table_name='crop_mix_recommendations')
    op.drop_index('ix_crop_mix_recs_farm', table_name='crop_mix_recommendations')
    op.drop_constraint('check_rec_fertilizer_non_negative', 'crop_mix_recommendations')
    op.drop_constraint('check_rec_labor_non_negative', 'crop_mix_recommendations')
    op.drop_constraint('check_rec_water_non_negative', 'crop_mix_recommendations')
    op.drop_constraint('check_rec_land_non_negative', 'crop_mix_recommendations')
    op.drop_constraint('check_rec_season', 'crop_mix_recommendations')
    op.drop_constraint('fk_crop_mix_recs_farm_id', 'crop_mix_recommendations')
    op.drop_column('crop_mix_recommendations', 'ai_synthesis_explanation')
    op.drop_column('crop_mix_recommendations', 'binding_constraints')
    op.drop_column('crop_mix_recommendations', 'net_profit_egp')
    op.drop_column('crop_mix_recommendations', 'total_fertilizer_cost_egp')
    op.drop_column('crop_mix_recommendations', 'total_labor_cost_egp')
    op.drop_column('crop_mix_recommendations', 'total_production_cost_egp')
    op.drop_column('crop_mix_recommendations', 'total_expected_revenue_egp')
    op.drop_column('crop_mix_recommendations', 'total_fertilizer_used_kg')
    op.drop_column('crop_mix_recommendations', 'total_labor_used_hours')
    op.drop_column('crop_mix_recommendations', 'total_water_used_m3')
    op.drop_column('crop_mix_recommendations', 'total_land_used_feddans')
    op.drop_column('crop_mix_recommendations', 'is_feasible')
    op.drop_column('crop_mix_recommendations', 'optimizer_version')
    op.drop_column('crop_mix_recommendations', 'season')
    op.drop_column('crop_mix_recommendations', 'farm_id')

    # Drop crop_rotation_matrix table
    op.drop_table('crop_rotation_matrix')

    # Drop crop_catalog table
    op.drop_index('ix_crop_catalog_farm_id', table_name='crop_catalog')
    op.drop_table('crop_catalog')

    # Reverse fields table changes
    op.drop_constraint('check_field_area_positive', 'fields')
    op.drop_constraint('check_field_organic_matter_non_negative', 'fields')
    op.drop_constraint('check_field_soil_texture', 'fields')
    op.drop_constraint('check_field_ec_non_negative', 'fields')
    op.drop_constraint('check_field_ph_range', 'fields')
    op.drop_column('fields', 'previous_crop_name')
    op.drop_column('fields', 'organic_matter_pct')
    op.drop_column('fields', 'soil_texture')
    op.drop_column('fields', 'soil_ec_ds_m')
    op.drop_column('fields', 'soil_ph')
    op.drop_column('fields', 'area_feddans')
    op.drop_column('fields', 'name_ar')
    op.drop_column('fields', 'name_en')

    # Reverse farms table changes
    op.drop_constraint('check_fertilizer_budget_non_negative', 'farms')
    op.drop_constraint('check_labor_budget_non_negative', 'farms')
    op.drop_constraint('check_water_budget_non_negative', 'farms')
    op.drop_constraint('check_farm_area_positive', 'farms')
    op.drop_constraint('check_farm_zone', 'farms')
    op.drop_column('farms', 'fertilizer_rate_egp_per_kg')
    op.drop_column('farms', 'labor_rate_egp_per_hour')
    op.drop_column('farms', 'fertilizer_budget_kg')
    op.drop_column('farms', 'labor_budget_hours')
    op.drop_column('farms', 'water_budget_m3')
    op.drop_column('farms', 'total_area_feddans')
    op.drop_column('farms', 'zone')