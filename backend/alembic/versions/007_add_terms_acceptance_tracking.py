"""add_terms_acceptance_tracking

Revision ID: 007
Revises: 006
Create Date: 2026-01-08

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    # Add terms acceptance tracking columns
    op.add_column('users', sa.Column('terms_accepted', sa.Boolean(), server_default='0', nullable=False))
    op.add_column('users', sa.Column('terms_accepted_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('terms_version', sa.String(), nullable=True))
    op.add_column('users', sa.Column('privacy_accepted', sa.Boolean(), server_default='0', nullable=False))
    op.add_column('users', sa.Column('privacy_accepted_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('privacy_version', sa.String(), nullable=True))


def downgrade():
    # Remove terms acceptance tracking columns
    op.drop_column('users', 'privacy_version')
    op.drop_column('users', 'privacy_accepted_at')
    op.drop_column('users', 'privacy_accepted')
    op.drop_column('users', 'terms_version')
    op.drop_column('users', 'terms_accepted_at')
    op.drop_column('users', 'terms_accepted')
