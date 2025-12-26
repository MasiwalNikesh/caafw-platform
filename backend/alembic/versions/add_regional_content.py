"""Add regional content tables and fields

Revision ID: add_regional_content
Revises: add_admin_dashboard
Create Date: 2025-01-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_regional_content'
down_revision: Union[str, None] = 'add_admin_dashboard'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create region type enum
    region_type_enum = postgresql.ENUM(
        'global', 'continent', 'country', 'state', 'city',
        name='regiontype',
        create_type=False
    )
    region_type_enum.create(op.get_bind(), checkfirst=True)

    # Create regional content type enum
    regional_content_type_enum = postgresql.ENUM(
        'job', 'event', 'news', 'product', 'research', 'learning', 'announcement', 'other',
        name='regionalcontenttype',
        create_type=False
    )
    regional_content_type_enum.create(op.get_bind(), checkfirst=True)

    # Create regions table
    op.create_table(
        'regions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(20), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False),
        sa.Column('region_type', sa.Enum('global', 'continent', 'country', 'state', 'city', name='regiontype'), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('iso_code', sa.String(3), nullable=True),
        sa.Column('timezone', sa.String(50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['parent_id'], ['regions.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('code'),
        sa.UniqueConstraint('slug')
    )
    op.create_index('ix_regions_code', 'regions', ['code'])
    op.create_index('ix_regions_slug', 'regions', ['slug'])
    op.create_index('idx_regions_parent', 'regions', ['parent_id'])
    op.create_index('idx_regions_type', 'regions', ['region_type'])
    op.create_index('idx_regions_active', 'regions', ['is_active'])

    # Create api_source_regions association table
    op.create_table(
        'api_source_regions',
        sa.Column('api_source_id', sa.Integer(), nullable=False),
        sa.Column('region_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('api_source_id', 'region_id'),
        sa.ForeignKeyConstraint(['api_source_id'], ['api_sources.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['region_id'], ['regions.id'], ondelete='CASCADE')
    )

    # Create regional_content table
    op.create_table(
        'regional_content',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('region_id', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.Enum('job', 'event', 'news', 'product', 'research', 'learning', 'announcement', 'other', name='regionalcontenttype'), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('slug', sa.String(550), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('url', sa.String(500), nullable=True),
        sa.Column('image_url', sa.String(500), nullable=True),
        sa.Column('data', postgresql.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_featured', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('moderation_status', sa.Enum('pending', 'approved', 'rejected', 'flagged', 'archived', name='contentstatus'), nullable=False, server_default='pending'),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.Column('updated_by_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['region_id'], ['regions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_by_id'], ['users.id'], ondelete='SET NULL')
    )
    op.create_index('ix_regional_content_slug', 'regional_content', ['slug'])
    op.create_index('idx_regional_content_region_type', 'regional_content', ['region_id', 'content_type'])
    op.create_index('idx_regional_content_status', 'regional_content', ['moderation_status'])
    op.create_index('idx_regional_content_active', 'regional_content', ['is_active'])
    op.create_index('idx_regional_content_featured', 'regional_content', ['is_featured'])

    # Add region_id to existing content tables
    op.add_column('jobs', sa.Column('region_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_jobs_region', 'jobs', 'regions', ['region_id'], ['id'], ondelete='SET NULL')

    op.add_column('events', sa.Column('region_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_events_region', 'events', 'regions', ['region_id'], ['id'], ondelete='SET NULL')

    op.add_column('news_articles', sa.Column('region_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_news_region', 'news_articles', 'regions', ['region_id'], ['id'], ondelete='SET NULL')

    op.add_column('products', sa.Column('region_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_products_region', 'products', 'regions', ['region_id'], ['id'], ondelete='SET NULL')

    op.add_column('research_papers', sa.Column('region_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_research_region', 'research_papers', 'regions', ['region_id'], ['id'], ondelete='SET NULL')

    op.add_column('learning_resources', sa.Column('region_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_learning_region', 'learning_resources', 'regions', ['region_id'], ['id'], ondelete='SET NULL')

    op.add_column('companies', sa.Column('region_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_companies_region', 'companies', 'regions', ['region_id'], ['id'], ondelete='SET NULL')

    # Seed initial regions
    op.execute("""
        INSERT INTO regions (code, name, slug, region_type, parent_id, iso_code, timezone, sort_order)
        VALUES
            ('GLOBAL', 'Global', 'global', 'global', NULL, NULL, 'UTC', 0);
    """)

    # Get the GLOBAL region id and insert continents
    op.execute("""
        INSERT INTO regions (code, name, slug, region_type, parent_id, iso_code, timezone, sort_order)
        SELECT 'NA', 'North America', 'north-america', 'continent', id, NULL, 'America/New_York', 1
        FROM regions WHERE code = 'GLOBAL';
    """)

    op.execute("""
        INSERT INTO regions (code, name, slug, region_type, parent_id, iso_code, timezone, sort_order)
        SELECT 'EU', 'Europe', 'europe', 'continent', id, NULL, 'Europe/London', 2
        FROM regions WHERE code = 'GLOBAL';
    """)

    op.execute("""
        INSERT INTO regions (code, name, slug, region_type, parent_id, iso_code, timezone, sort_order)
        SELECT 'ASIA', 'Asia', 'asia', 'continent', id, NULL, 'Asia/Tokyo', 3
        FROM regions WHERE code = 'GLOBAL';
    """)

    # Insert countries under North America
    op.execute("""
        INSERT INTO regions (code, name, slug, region_type, parent_id, iso_code, timezone, sort_order)
        SELECT 'US', 'United States', 'united-states', 'country', id, 'USA', 'America/New_York', 1
        FROM regions WHERE code = 'NA';
    """)

    op.execute("""
        INSERT INTO regions (code, name, slug, region_type, parent_id, iso_code, timezone, sort_order)
        SELECT 'CA', 'Canada', 'canada', 'country', id, 'CAN', 'America/Toronto', 2
        FROM regions WHERE code = 'NA';
    """)

    # Insert countries under Europe
    op.execute("""
        INSERT INTO regions (code, name, slug, region_type, parent_id, iso_code, timezone, sort_order)
        SELECT 'UK', 'United Kingdom', 'united-kingdom', 'country', id, 'GBR', 'Europe/London', 1
        FROM regions WHERE code = 'EU';
    """)

    op.execute("""
        INSERT INTO regions (code, name, slug, region_type, parent_id, iso_code, timezone, sort_order)
        SELECT 'DE', 'Germany', 'germany', 'country', id, 'DEU', 'Europe/Berlin', 2
        FROM regions WHERE code = 'EU';
    """)

    op.execute("""
        INSERT INTO regions (code, name, slug, region_type, parent_id, iso_code, timezone, sort_order)
        SELECT 'FR', 'France', 'france', 'country', id, 'FRA', 'Europe/Paris', 3
        FROM regions WHERE code = 'EU';
    """)

    # Insert countries under Asia
    op.execute("""
        INSERT INTO regions (code, name, slug, region_type, parent_id, iso_code, timezone, sort_order)
        SELECT 'CN', 'China', 'china', 'country', id, 'CHN', 'Asia/Shanghai', 1
        FROM regions WHERE code = 'ASIA';
    """)

    op.execute("""
        INSERT INTO regions (code, name, slug, region_type, parent_id, iso_code, timezone, sort_order)
        SELECT 'JP', 'Japan', 'japan', 'country', id, 'JPN', 'Asia/Tokyo', 2
        FROM regions WHERE code = 'ASIA';
    """)

    op.execute("""
        INSERT INTO regions (code, name, slug, region_type, parent_id, iso_code, timezone, sort_order)
        SELECT 'IN', 'India', 'india', 'country', id, 'IND', 'Asia/Kolkata', 3
        FROM regions WHERE code = 'ASIA';
    """)

    op.execute("""
        INSERT INTO regions (code, name, slug, region_type, parent_id, iso_code, timezone, sort_order)
        SELECT 'KR', 'South Korea', 'south-korea', 'country', id, 'KOR', 'Asia/Seoul', 4
        FROM regions WHERE code = 'ASIA';
    """)

    op.execute("""
        INSERT INTO regions (code, name, slug, region_type, parent_id, iso_code, timezone, sort_order)
        SELECT 'SG', 'Singapore', 'singapore', 'country', id, 'SGP', 'Asia/Singapore', 5
        FROM regions WHERE code = 'ASIA';
    """)


def downgrade() -> None:
    # Remove region_id from content tables
    op.drop_constraint('fk_companies_region', 'companies', type_='foreignkey')
    op.drop_column('companies', 'region_id')

    op.drop_constraint('fk_learning_region', 'learning_resources', type_='foreignkey')
    op.drop_column('learning_resources', 'region_id')

    op.drop_constraint('fk_research_region', 'research_papers', type_='foreignkey')
    op.drop_column('research_papers', 'region_id')

    op.drop_constraint('fk_products_region', 'products', type_='foreignkey')
    op.drop_column('products', 'region_id')

    op.drop_constraint('fk_news_region', 'news_articles', type_='foreignkey')
    op.drop_column('news_articles', 'region_id')

    op.drop_constraint('fk_events_region', 'events', type_='foreignkey')
    op.drop_column('events', 'region_id')

    op.drop_constraint('fk_jobs_region', 'jobs', type_='foreignkey')
    op.drop_column('jobs', 'region_id')

    # Drop regional_content table
    op.drop_index('idx_regional_content_featured', 'regional_content')
    op.drop_index('idx_regional_content_active', 'regional_content')
    op.drop_index('idx_regional_content_status', 'regional_content')
    op.drop_index('idx_regional_content_region_type', 'regional_content')
    op.drop_index('ix_regional_content_slug', 'regional_content')
    op.drop_table('regional_content')

    # Drop api_source_regions table
    op.drop_table('api_source_regions')

    # Drop regions table
    op.drop_index('idx_regions_active', 'regions')
    op.drop_index('idx_regions_type', 'regions')
    op.drop_index('idx_regions_parent', 'regions')
    op.drop_index('ix_regions_slug', 'regions')
    op.drop_index('ix_regions_code', 'regions')
    op.drop_table('regions')

    # Drop enums
    regional_content_type_enum = postgresql.ENUM(
        'job', 'event', 'news', 'product', 'research', 'learning', 'announcement', 'other',
        name='regionalcontenttype'
    )
    regional_content_type_enum.drop(op.get_bind(), checkfirst=True)

    region_type_enum = postgresql.ENUM(
        'global', 'continent', 'country', 'state', 'city',
        name='regiontype'
    )
    region_type_enum.drop(op.get_bind(), checkfirst=True)
