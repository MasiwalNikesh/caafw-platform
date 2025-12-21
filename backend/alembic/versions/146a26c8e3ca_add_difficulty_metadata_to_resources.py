"""add_difficulty_metadata_to_resources

Revision ID: 146a26c8e3ca
Revises: 11c894af15be
Create Date: 2025-12-21 12:33:25.450912

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '146a26c8e3ca'
down_revision: Union[str, None] = '11c894af15be'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add difficulty metadata to learning_resources
    op.add_column('learning_resources',
                  sa.Column('source_difficulty', sa.String(length=50), nullable=True))
    op.add_column('learning_resources',
                  sa.Column('prerequisites', sa.JSON(), nullable=True))
    op.add_column('learning_resources',
                  sa.Column('is_beginner_friendly', sa.Boolean(), nullable=True, server_default='false'))

    # Add difficulty metadata to events
    op.add_column('events',
                  sa.Column('source_difficulty', sa.String(length=50), nullable=True))
    op.add_column('events',
                  sa.Column('is_beginner_friendly', sa.Boolean(), nullable=True, server_default='false'))

    # Add beginner-friendly flag to jobs
    op.add_column('jobs',
                  sa.Column('is_beginner_friendly', sa.Boolean(), nullable=True, server_default='false'))

    # Create index for beginner-friendly filtering
    op.create_index('idx_learning_beginner_friendly', 'learning_resources', ['is_beginner_friendly'])
    op.create_index('idx_events_beginner_friendly', 'events', ['is_beginner_friendly'])
    op.create_index('idx_jobs_beginner_friendly', 'jobs', ['is_beginner_friendly'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_jobs_beginner_friendly', table_name='jobs')
    op.drop_index('idx_events_beginner_friendly', table_name='events')
    op.drop_index('idx_learning_beginner_friendly', table_name='learning_resources')

    # Drop columns from jobs
    op.drop_column('jobs', 'is_beginner_friendly')

    # Drop columns from events
    op.drop_column('events', 'is_beginner_friendly')
    op.drop_column('events', 'source_difficulty')

    # Drop columns from learning_resources
    op.drop_column('learning_resources', 'is_beginner_friendly')
    op.drop_column('learning_resources', 'prerequisites')
    op.drop_column('learning_resources', 'source_difficulty')
