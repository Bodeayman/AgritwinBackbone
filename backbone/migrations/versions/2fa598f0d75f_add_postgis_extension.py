"""add postgis extension

Revision ID: 2fa598f0d75f
Revises: 30d9403fe7e2
Create Date: 2026-08-08 19:22:26.589311

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2fa598f0d75f'
down_revision: Union[str, None] = '30d9403fe7e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
