"""add_domain_to_users

Revision ID: 001
Revises: 
Create Date: 2025-11-27 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add domain column to users table
    op.add_column('users', sa.Column('domain', sa.String(length=50), nullable=True))
    
    # Create unique index on domain column
    op.create_index(op.f('ix_users_domain'), 'users', ['domain'], unique=True)


def downgrade() -> None:
    # Drop index and column
    op.drop_index(op.f('ix_users_domain'), table_name='users')
    op.drop_column('users', 'domain')
