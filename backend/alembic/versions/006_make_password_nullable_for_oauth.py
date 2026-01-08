"""make_hashed_password_nullable_for_oauth

Revision ID: 006
Revises: 005
Create Date: 2026-01-08

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    # Make hashed_password nullable to support OAuth users
    op.alter_column('users', 'hashed_password',
                    existing_type=sa.String(),
                    nullable=True)


def downgrade():
    # Revert to non-nullable
    op.alter_column('users', 'hashed_password',
                    existing_type=sa.String(),
                    nullable=False)
