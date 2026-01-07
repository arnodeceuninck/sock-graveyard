"""add user sequence ids

Revision ID: 005
Revises: 004
Create Date: 2026-01-07

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    # For SQLite, we need to use batch operations to alter columns
    with op.batch_alter_table('socks') as batch_op:
        batch_op.add_column(sa.Column('user_sequence_id', sa.Integer(), nullable=True))
    
    # Populate user_sequence_id for existing socks using SQLite syntax
    # SQLite doesn't have window functions in older versions, so we'll use a different approach
    op.execute("""
        UPDATE socks
        SET user_sequence_id = (
            SELECT COUNT(*) 
            FROM socks AS s2 
            WHERE s2.owner_id = socks.owner_id 
            AND (s2.created_at < socks.created_at OR (s2.created_at = socks.created_at AND s2.id <= socks.id))
        )
    """)
    
    # For matches, we need to add columns first
    with op.batch_alter_table('matches') as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('user_sequence_id', sa.Integer(), nullable=True))
    
    # Populate user_id for existing matches based on sock ownership
    op.execute("""
        UPDATE matches
        SET user_id = (SELECT owner_id FROM socks WHERE socks.id = matches.sock1_id)
    """)
    
    # Populate user_sequence_id for existing matches
    op.execute("""
        UPDATE matches
        SET user_sequence_id = (
            SELECT COUNT(*) 
            FROM matches AS m2 
            WHERE m2.user_id = matches.user_id 
            AND (m2.matched_at < matches.matched_at OR (m2.matched_at = matches.matched_at AND m2.id <= matches.id))
        )
    """)
    
    # Now recreate tables with non-nullable constraints using batch operations
    # This is necessary for SQLite to enforce NOT NULL
    with op.batch_alter_table('socks') as batch_op:
        batch_op.alter_column('user_sequence_id', nullable=False)
    
    with op.batch_alter_table('matches') as batch_op:
        batch_op.alter_column('user_id', nullable=False)
        batch_op.alter_column('user_sequence_id', nullable=False)
        batch_op.create_foreign_key('fk_matches_user_id', 'users', ['user_id'], ['id'])


def downgrade():
    # Drop foreign key constraint
    op.drop_constraint('fk_matches_user_id', 'matches', type_='foreignkey')
    
    # Drop columns
    op.drop_column('matches', 'user_sequence_id')
    op.drop_column('matches', 'user_id')
    op.drop_column('socks', 'user_sequence_id')
