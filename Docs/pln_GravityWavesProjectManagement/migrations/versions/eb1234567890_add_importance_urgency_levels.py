"""Add importance_levels and urgency_levels tables

Revision ID: eb1234567890
Revises: ea942e2296e4
Create Date: 2025-06-12 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eb1234567890'
down_revision = 'ea942e2296e4'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('importance_levels',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('level', sa.Integer(), nullable=False, unique=True),
        sa.Column('description', sa.String(length=100), nullable=False)
    )
    op.create_table('urgency_levels',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('level', sa.Integer(), nullable=False, unique=True),
        sa.Column('description', sa.String(length=100), nullable=False)
    )


def downgrade():
    op.drop_table('urgency_levels')
    op.drop_table('importance_levels')
