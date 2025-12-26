"""Add admin dashboard tables and moderation fields

Revision ID: add_admin_dashboard
Revises: db16ba70f1a1
Create Date: 2025-01-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_admin_dashboard'
down_revision: Union[str, None] = 'db16ba70f1a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enums
    user_role_enum = postgresql.ENUM(
        'user', 'moderator', 'admin', 'super_admin',
        name='userrole',
        create_type=False
    )
    user_role_enum.create(op.get_bind(), checkfirst=True)

    content_status_enum = postgresql.ENUM(
        'pending', 'approved', 'rejected', 'flagged', 'archived',
        name='contentstatus',
        create_type=False
    )
    content_status_enum.create(op.get_bind(), checkfirst=True)

    # Add role and ban fields to users table
    op.add_column('users', sa.Column('role', sa.Enum('user', 'moderator', 'admin', 'super_admin', name='userrole'), nullable=False, server_default='user'))
    op.add_column('users', sa.Column('is_banned', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('banned_reason', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('banned_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('banned_by_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_users_banned_by', 'users', 'users', ['banned_by_id'], ['id'])

    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('slug', sa.String(50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('color', sa.String(7), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_featured', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('slug')
    )
    op.create_index('ix_tags_slug', 'tags', ['slug'])

    # Create content_tags table
    op.create_table(
        'content_tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(50), nullable=False),
        sa.Column('content_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE')
    )
    op.create_index('idx_content_tags_lookup', 'content_tags', ['content_type', 'content_id'])
    op.create_index('idx_content_tags_unique', 'content_tags', ['tag_id', 'content_type', 'content_id'], unique=True)

    # Create content_categories table
    op.create_table(
        'content_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('icon', sa.String(50), nullable=True),
        sa.Column('color', sa.String(7), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['parent_id'], ['content_categories.id']),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('slug')
    )
    op.create_index('ix_content_categories_slug', 'content_categories', ['slug'])

    # Create content_category_assignments table
    op.create_table(
        'content_category_assignments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(50), nullable=False),
        sa.Column('content_id', sa.Integer(), nullable=False),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['category_id'], ['content_categories.id'], ondelete='CASCADE')
    )
    op.create_index('idx_category_assignments_lookup', 'content_category_assignments', ['content_type', 'content_id'])
    op.create_index('idx_category_assignments_unique', 'content_category_assignments', ['category_id', 'content_type', 'content_id'], unique=True)

    # Create admin_audit_logs table
    op.create_table(
        'admin_audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admin_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('old_values', postgresql.JSON(), nullable=True),
        sa.Column('new_values', postgresql.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['admin_id'], ['users.id'])
    )
    op.create_index('idx_audit_log_admin', 'admin_audit_logs', ['admin_id'])
    op.create_index('idx_audit_log_entity', 'admin_audit_logs', ['entity_type', 'entity_id'])
    op.create_index('idx_audit_log_created', 'admin_audit_logs', ['created_at'])

    # Create api_sources table
    op.create_table(
        'api_sources',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False),
        sa.Column('source_type', sa.String(50), nullable=False),
        sa.Column('url', sa.String(500), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('requires_api_key', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('auto_approve', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('fetch_frequency', sa.Integer(), nullable=False, server_default='360'),
        sa.Column('last_fetched_at', sa.DateTime(), nullable=True),
        sa.Column('last_success_at', sa.DateTime(), nullable=True),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('error_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('items_fetched', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('config', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index('ix_api_sources_slug', 'api_sources', ['slug'])

    # Create content_moderation_history table
    op.create_table(
        'content_moderation_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(50), nullable=False),
        sa.Column('content_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('previous_status', sa.String(20), nullable=True),
        sa.Column('new_status', sa.String(20), nullable=False),
        sa.Column('reviewed_by', sa.Integer(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'])
    )
    op.create_index('idx_moderation_history_content', 'content_moderation_history', ['content_type', 'content_id'])
    op.create_index('idx_moderation_history_reviewer', 'content_moderation_history', ['reviewed_by'])

    # Add moderation fields to news_articles
    op.add_column('news_articles', sa.Column('moderation_status', sa.Enum('pending', 'approved', 'rejected', 'flagged', 'archived', name='contentstatus'), nullable=False, server_default='pending'))
    op.add_column('news_articles', sa.Column('reviewed_by_id', sa.Integer(), nullable=True))
    op.add_column('news_articles', sa.Column('reviewed_at', sa.DateTime(), nullable=True))
    op.add_column('news_articles', sa.Column('rejection_reason', sa.Text(), nullable=True))
    op.create_index('ix_news_articles_moderation_status', 'news_articles', ['moderation_status'])
    op.create_foreign_key('fk_news_reviewed_by', 'news_articles', 'users', ['reviewed_by_id'], ['id'])

    # Add moderation fields to jobs
    op.add_column('jobs', sa.Column('moderation_status', sa.Enum('pending', 'approved', 'rejected', 'flagged', 'archived', name='contentstatus'), nullable=False, server_default='pending'))
    op.add_column('jobs', sa.Column('reviewed_by_id', sa.Integer(), nullable=True))
    op.add_column('jobs', sa.Column('reviewed_at', sa.DateTime(), nullable=True))
    op.add_column('jobs', sa.Column('rejection_reason', sa.Text(), nullable=True))
    op.create_index('ix_jobs_moderation_status', 'jobs', ['moderation_status'])
    op.create_foreign_key('fk_jobs_reviewed_by', 'jobs', 'users', ['reviewed_by_id'], ['id'])

    # Add moderation fields to products
    op.add_column('products', sa.Column('moderation_status', sa.Enum('pending', 'approved', 'rejected', 'flagged', 'archived', name='contentstatus'), nullable=False, server_default='pending'))
    op.add_column('products', sa.Column('reviewed_by_id', sa.Integer(), nullable=True))
    op.add_column('products', sa.Column('reviewed_at', sa.DateTime(), nullable=True))
    op.add_column('products', sa.Column('rejection_reason', sa.Text(), nullable=True))
    op.create_index('ix_products_moderation_status', 'products', ['moderation_status'])
    op.create_foreign_key('fk_products_reviewed_by', 'products', 'users', ['reviewed_by_id'], ['id'])

    # Add moderation fields to events (rename status to event_status first)
    op.alter_column('events', 'status', new_column_name='event_status')
    op.add_column('events', sa.Column('moderation_status', sa.Enum('pending', 'approved', 'rejected', 'flagged', 'archived', name='contentstatus'), nullable=False, server_default='pending'))
    op.add_column('events', sa.Column('reviewed_by_id', sa.Integer(), nullable=True))
    op.add_column('events', sa.Column('reviewed_at', sa.DateTime(), nullable=True))
    op.add_column('events', sa.Column('rejection_reason', sa.Text(), nullable=True))
    op.create_index('ix_events_moderation_status', 'events', ['moderation_status'])
    op.create_foreign_key('fk_events_reviewed_by', 'events', 'users', ['reviewed_by_id'], ['id'])

    # Add moderation fields to research_papers (default to approved for arXiv)
    op.add_column('research_papers', sa.Column('moderation_status', sa.Enum('pending', 'approved', 'rejected', 'flagged', 'archived', name='contentstatus'), nullable=False, server_default='approved'))
    op.add_column('research_papers', sa.Column('reviewed_by_id', sa.Integer(), nullable=True))
    op.add_column('research_papers', sa.Column('reviewed_at', sa.DateTime(), nullable=True))
    op.add_column('research_papers', sa.Column('rejection_reason', sa.Text(), nullable=True))
    op.create_index('ix_research_papers_moderation_status', 'research_papers', ['moderation_status'])
    op.create_foreign_key('fk_research_reviewed_by', 'research_papers', 'users', ['reviewed_by_id'], ['id'])


def downgrade() -> None:
    # Remove moderation fields from research_papers
    op.drop_constraint('fk_research_reviewed_by', 'research_papers', type_='foreignkey')
    op.drop_index('ix_research_papers_moderation_status', 'research_papers')
    op.drop_column('research_papers', 'rejection_reason')
    op.drop_column('research_papers', 'reviewed_at')
    op.drop_column('research_papers', 'reviewed_by_id')
    op.drop_column('research_papers', 'moderation_status')

    # Remove moderation fields from events
    op.drop_constraint('fk_events_reviewed_by', 'events', type_='foreignkey')
    op.drop_index('ix_events_moderation_status', 'events')
    op.drop_column('events', 'rejection_reason')
    op.drop_column('events', 'reviewed_at')
    op.drop_column('events', 'reviewed_by_id')
    op.drop_column('events', 'moderation_status')
    op.alter_column('events', 'event_status', new_column_name='status')

    # Remove moderation fields from products
    op.drop_constraint('fk_products_reviewed_by', 'products', type_='foreignkey')
    op.drop_index('ix_products_moderation_status', 'products')
    op.drop_column('products', 'rejection_reason')
    op.drop_column('products', 'reviewed_at')
    op.drop_column('products', 'reviewed_by_id')
    op.drop_column('products', 'moderation_status')

    # Remove moderation fields from jobs
    op.drop_constraint('fk_jobs_reviewed_by', 'jobs', type_='foreignkey')
    op.drop_index('ix_jobs_moderation_status', 'jobs')
    op.drop_column('jobs', 'rejection_reason')
    op.drop_column('jobs', 'reviewed_at')
    op.drop_column('jobs', 'reviewed_by_id')
    op.drop_column('jobs', 'moderation_status')

    # Remove moderation fields from news_articles
    op.drop_constraint('fk_news_reviewed_by', 'news_articles', type_='foreignkey')
    op.drop_index('ix_news_articles_moderation_status', 'news_articles')
    op.drop_column('news_articles', 'rejection_reason')
    op.drop_column('news_articles', 'reviewed_at')
    op.drop_column('news_articles', 'reviewed_by_id')
    op.drop_column('news_articles', 'moderation_status')

    # Drop content_moderation_history table
    op.drop_index('idx_moderation_history_reviewer', 'content_moderation_history')
    op.drop_index('idx_moderation_history_content', 'content_moderation_history')
    op.drop_table('content_moderation_history')

    # Drop api_sources table
    op.drop_index('ix_api_sources_slug', 'api_sources')
    op.drop_table('api_sources')

    # Drop admin_audit_logs table
    op.drop_index('idx_audit_log_created', 'admin_audit_logs')
    op.drop_index('idx_audit_log_entity', 'admin_audit_logs')
    op.drop_index('idx_audit_log_admin', 'admin_audit_logs')
    op.drop_table('admin_audit_logs')

    # Drop content_category_assignments table
    op.drop_index('idx_category_assignments_unique', 'content_category_assignments')
    op.drop_index('idx_category_assignments_lookup', 'content_category_assignments')
    op.drop_table('content_category_assignments')

    # Drop content_categories table
    op.drop_index('ix_content_categories_slug', 'content_categories')
    op.drop_table('content_categories')

    # Drop content_tags table
    op.drop_index('idx_content_tags_unique', 'content_tags')
    op.drop_index('idx_content_tags_lookup', 'content_tags')
    op.drop_table('content_tags')

    # Drop tags table
    op.drop_index('ix_tags_slug', 'tags')
    op.drop_table('tags')

    # Remove role and ban fields from users
    op.drop_constraint('fk_users_banned_by', 'users', type_='foreignkey')
    op.drop_column('users', 'banned_by_id')
    op.drop_column('users', 'banned_at')
    op.drop_column('users', 'banned_reason')
    op.drop_column('users', 'is_banned')
    op.drop_column('users', 'role')

    # Drop enums
    content_status_enum = postgresql.ENUM(
        'pending', 'approved', 'rejected', 'flagged', 'archived',
        name='contentstatus'
    )
    content_status_enum.drop(op.get_bind(), checkfirst=True)

    user_role_enum = postgresql.ENUM(
        'user', 'moderator', 'admin', 'super_admin',
        name='userrole'
    )
    user_role_enum.drop(op.get_bind(), checkfirst=True)
