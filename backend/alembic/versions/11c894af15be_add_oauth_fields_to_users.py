"""add_oauth_fields_to_users

Revision ID: 11c894af15be
Revises: 2adafff8602a
Create Date: 2025-12-21 12:26:14.714684

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '11c894af15be'
down_revision: Union[str, None] = '2adafff8602a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add OAuth columns to users table
    op.add_column('users', sa.Column('oauth_provider', sa.String(length=20), nullable=True))
    op.add_column('users', sa.Column('oauth_id', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('oauth_email_verified', sa.Boolean(), nullable=True, server_default='false'))

    # Make password_hash nullable for OAuth users
    op.alter_column('users', 'password_hash',
                    existing_type=sa.String(),
                    nullable=True)

    # Create unique index for OAuth provider and ID combination
    op.create_index('idx_oauth_provider_id', 'users', ['oauth_provider', 'oauth_id'], unique=True)


def downgrade() -> None:
    # Drop the OAuth index
    op.drop_index('idx_oauth_provider_id', table_name='users')

    # Make password_hash NOT NULL again
    op.alter_column('users', 'password_hash',
                    existing_type=sa.String(),
                    nullable=False)

    # Drop OAuth columns
    op.drop_column('users', 'oauth_email_verified')
    op.drop_column('users', 'oauth_id')
    op.drop_column('users', 'oauth_provider')
