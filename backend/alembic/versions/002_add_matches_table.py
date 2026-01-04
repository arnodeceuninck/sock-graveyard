"""add matches table

Revision ID: 002
Revises: 001
Create Date: 2026-01-04

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Create matches table
    op.create_table(
        'matches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sock1_id', sa.Integer(), nullable=False),
        sa.Column('sock2_id', sa.Integer(), nullable=False),
        sa.Column('matched_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['sock1_id'], ['socks.id'], ),
        sa.ForeignKeyConstraint(['sock2_id'], ['socks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_matches_sock1_id'), 'matches', ['sock1_id'], unique=False)
    op.create_index(op.f('ix_matches_sock2_id'), 'matches', ['sock2_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_matches_sock2_id'), table_name='matches')
    op.drop_index(op.f('ix_matches_sock1_id'), table_name='matches')
    op.drop_table('matches')
