"""Add content progress table

Revision ID: add_content_progress
Revises: add_bookmarks_tables
Create Date: 2024-12-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_content_progress'
down_revision: Union[str, None] = 'add_bookmarks_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'content_progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(50), nullable=False),
        sa.Column('content_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(20), default='not_started', nullable=False),
        sa.Column('progress_percentage', sa.Integer(), default=0, nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_accessed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('time_spent', sa.Integer(), default=0, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'content_type', 'content_id', name='unique_user_content_progress'),
    )
    op.create_index('ix_content_progress_id', 'content_progress', ['id'])
    op.create_index('ix_content_progress_user_id', 'content_progress', ['user_id'])
    op.create_index('ix_content_progress_content_type', 'content_progress', ['content_type'])
    op.create_index('ix_content_progress_content_id', 'content_progress', ['content_id'])
    op.create_index('idx_progress_content', 'content_progress', ['content_type', 'content_id'])
    op.create_index('idx_progress_user_status', 'content_progress', ['user_id', 'status'])


def downgrade() -> None:
    op.drop_table('content_progress')

