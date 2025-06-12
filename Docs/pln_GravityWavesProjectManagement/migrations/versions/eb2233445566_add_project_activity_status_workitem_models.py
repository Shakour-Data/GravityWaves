"""Add Project, Activity, Status, WorkItem models and project_id to Task

Revision ID: eb2233445566
Revises: eb1234567890
Create Date: 2025-06-12 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'eb2233445566'
down_revision = 'eb1234567890'
branch_labels = None
depends_on = None

def upgrade():
    # Add project_id column to tasks table
    op.add_column('tasks', sa.Column('project_id', sa.Integer(), nullable=False))
    op.create_foreign_key('fk_tasks_project_id_projects', 'tasks', 'projects', ['project_id'], ['id'])

    # Create projects table
    op.create_table('projects',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parent_id', sa.Integer(), sa.ForeignKey('projects.id'), nullable=True)
    )

    # Create activities table
    op.create_table('activities',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('task_id', sa.Integer(), sa.ForeignKey('tasks.id'), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True)
    )

    # Create statuses table
    op.create_table('statuses',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('activity_id', sa.Integer(), sa.ForeignKey('activities.id'), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False)
    )

    # Create work_items table
    op.create_table('work_items',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('status_id', sa.Integer(), sa.ForeignKey('statuses.id'), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('importance', sa.Integer(), nullable=False, default=1),
        sa.Column('urgency', sa.Integer(), nullable=False, default=1),
        sa.Column('assigned_resource_id', sa.Integer(), sa.ForeignKey('resources.id'), nullable=False)
    )

def downgrade():
    op.drop_table('work_items')
    op.drop_table('statuses')
    op.drop_table('activities')
    op.drop_table('projects')
    op.drop_constraint('fk_tasks_project_id_projects', 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'project_id')
