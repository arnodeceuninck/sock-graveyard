"""Replace username with email

Revision ID: 004
Revises: 003
Create Date: 2026-01-07

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Rename username column to email in users table
    op.alter_column('users', 'username', new_column_name='email')
    
    # Rename the index
    op.drop_index('ix_users_username', table_name='users')
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)


def downgrade() -> None:
    # Revert email back to username
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.alter_column('users', 'email', new_column_name='username')
