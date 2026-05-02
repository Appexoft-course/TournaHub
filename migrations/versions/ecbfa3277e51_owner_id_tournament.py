from alembic import op
import sqlalchemy as sa

revision = 'ecbfa3277e51'
down_revision = 'a872b22e5273'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('tournaments', sa.Column('owner_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'tournaments', 'users', ['owner_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    op.drop_constraint(None, 'tournaments', type_='foreignkey')
    op.drop_column('tournaments', 'owner_id')