"""add_learning_paths_and_progress

Revision ID: db16ba70f1a1
Revises: 146a26c8e3ca
Create Date: 2025-12-21 12:38:53.351112

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'db16ba70f1a1'
down_revision: Union[str, None] = '146a26c8e3ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create learning_paths table
    op.create_table(
        'learning_paths',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=300), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('level', sa.String(length=20), nullable=False),  # novice, beginner, intermediate, expert
        sa.Column('duration_hours', sa.Integer(), nullable=True),
        sa.Column('topics', sa.JSON(), nullable=True),
        sa.Column('resource_ids', sa.JSON(), nullable=False),  # Ordered array of resource IDs
        sa.Column('is_featured', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )

    # Create user_learning_progress table
    op.create_table(
        'user_learning_progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('path_id', sa.Integer(), nullable=False),
        sa.Column('completed_resource_ids', sa.JSON(), nullable=True, server_default='[]'),
        sa.Column('current_resource_id', sa.Integer(), nullable=True),
        sa.Column('progress_percentage', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('last_activity_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['path_id'], ['learning_paths.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'path_id', name='uq_user_path')
    )

    # Create indexes
    op.create_index('idx_learning_paths_level', 'learning_paths', ['level'])
    op.create_index('idx_learning_paths_featured', 'learning_paths', ['is_featured'])
    op.create_index('idx_user_progress_user', 'user_learning_progress', ['user_id'])
    op.create_index('idx_user_progress_path', 'user_learning_progress', ['path_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_user_progress_path', table_name='user_learning_progress')
    op.drop_index('idx_user_progress_user', table_name='user_learning_progress')
    op.drop_index('idx_learning_paths_featured', table_name='learning_paths')
    op.drop_index('idx_learning_paths_level', table_name='learning_paths')

    # Drop tables
    op.drop_table('user_learning_progress')
    op.drop_table('learning_paths')
