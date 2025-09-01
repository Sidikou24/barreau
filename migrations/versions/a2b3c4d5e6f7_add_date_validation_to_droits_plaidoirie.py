"""Add date_validation column to droits_plaidoirie

Revision ID: a2b3c4d5e6f7
Revises: 91d0163910e3
Create Date: 2025-08-28 12:30:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a2b3c4d5e6f7'
down_revision = '91d0163910e3'
branch_labels = None
depends_on = None


def upgrade():
    # Add date_validation column
    op.add_column('droits_plaidoirie', sa.Column('date_validation', sa.DateTime(), nullable=True))


def downgrade():
    # Remove date_validation column
    op.drop_column('droits_plaidoirie', 'date_validation')
