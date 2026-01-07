"""add image_no_bg_path to socks

Revision ID: 003
Revises: 002
Create Date: 2026-01-07

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add image_no_bg_path column to socks table
    op.add_column('socks', sa.Column('image_no_bg_path', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove image_no_bg_path column from socks table
    op.drop_column('socks', 'image_no_bg_path')
