from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY

revision = 'c3d4e5f6a7b8'
down_revision = 'ecbfa3277e51'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column('tournaments', 'game_type')
    op.add_column('tournaments', sa.Column('game_type', ARRAY(sa.String()), nullable=False, server_default='{}'))


def downgrade() -> None:
    op.drop_column('tournaments', 'game_type')
    op.add_column('tournaments', sa.Column('game_type', sa.String(100), nullable=False, server_default=''))