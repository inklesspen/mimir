"""Add author to writeup

Revision ID: 41d36feab50
Revises: 35b41a74130
Create Date: 2016-02-22 02:08:17.978077

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '41d36feab50'
down_revision = '35b41a74130'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('writeups', sa.Column('author', sa.Unicode(length=100), nullable=True))
    t_w = sa.table(
        'writeups',
        sa.column('id', sa.Integer),
        sa.column('author', sa.String),
    )
    t_wp = sa.table(
        'writeup_posts',
        sa.column('writeup_id', sa.Integer),
        sa.column('author', sa.String),
        sa.column('index', sa.Integer),
    )
    stmt = sa.select([t_wp.c.author]).where(sa.and_(t_wp.c.writeup_id == t_w.c.id, t_wp.c.index == 1))
    op.execute(t_w.update().values(author=stmt))
    op.alter_column('writeups', 'author', nullable=False)


def downgrade():
    op.drop_column('writeups', 'author')
