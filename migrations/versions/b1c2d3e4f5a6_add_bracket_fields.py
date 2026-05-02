"""add bracket fields to matches and tournaments

Revision ID: b1c2d3e4f5a6
Revises: c3d4e5f6a7b8
Create Date: 2025-05-01
"""

from alembic import op
import sqlalchemy as sa

revision = 'b1c2d3e4f5a6'
down_revision = 'c3d4e5f6a7b8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('matches', sa.Column('tournament_id', sa.Integer(), nullable=True))
    op.add_column('matches', sa.Column('round', sa.Integer(), nullable=True))
    op.add_column('matches', sa.Column('match_index', sa.Integer(), nullable=True))
    op.add_column('matches', sa.Column('slot_top_id', sa.String(), nullable=True))
    op.add_column('matches', sa.Column('slot_bottom_id', sa.String(), nullable=True))
    op.add_column('matches', sa.Column('player1_id', sa.Integer(), nullable=True))
    op.add_column('matches', sa.Column('player2_id', sa.Integer(), nullable=True))
    op.add_column('matches', sa.Column('bracket_winner_id', sa.Integer(), nullable=True))
    op.add_column('matches', sa.Column('status', sa.String(), nullable=False, server_default='pending'))

    op.create_foreign_key('fk_matches_tournament_id', 'matches', 'tournaments', ['tournament_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_matches_player1_id', 'matches', 'users', ['player1_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('fk_matches_player2_id', 'matches', 'users', ['player2_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('fk_matches_bracket_winner_id', 'matches', 'users', ['bracket_winner_id'], ['id'], ondelete='SET NULL')

    op.create_index('ix_matches_tournament_round', 'matches', ['tournament_id', 'round', 'match_index'])

    op.add_column('tournaments', sa.Column('status', sa.String(50), nullable=False, server_default='created'))


def downgrade() -> None:
    op.drop_column('tournaments', 'status')

    op.drop_index('ix_matches_tournament_round', table_name='matches')
    op.drop_constraint('fk_matches_bracket_winner_id', 'matches', type_='foreignkey')
    op.drop_constraint('fk_matches_player2_id', 'matches', type_='foreignkey')
    op.drop_constraint('fk_matches_player1_id', 'matches', type_='foreignkey')
    op.drop_constraint('fk_matches_tournament_id', 'matches', type_='foreignkey')

    op.drop_column('matches', 'status')
    op.drop_column('matches', 'bracket_winner_id')
    op.drop_column('matches', 'player2_id')
    op.drop_column('matches', 'player1_id')
    op.drop_column('matches', 'slot_bottom_id')
    op.drop_column('matches', 'slot_top_id')
    op.drop_column('matches', 'match_index')
    op.drop_column('matches', 'round')
    op.drop_column('matches', 'tournament_id')