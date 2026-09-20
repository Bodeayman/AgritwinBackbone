"""add_fk_crop_cycles_field_id

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-08-10 19:12:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add the missing FK constraint: crop_cycles.field_id -> fields.id CASCADE
    op.create_foreign_key(
        'fk_crop_cycles_field_id',
        'crop_cycles',
        'fields',
        ['field_id'],
        ['id'],
        ondelete='CASCADE',
    )


def downgrade() -> None:
    op.drop_constraint('fk_crop_cycles_field_id', 'crop_cycles', type_='foreignkey')
