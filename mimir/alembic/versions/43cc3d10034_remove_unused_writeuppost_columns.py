"""Remove unused WriteupPost columns

Revision ID: 43cc3d10034
Revises: 2675bc6512c
Create Date: 2015-12-06 15:59:11.359448

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '43cc3d10034'
down_revision = '2675bc6512c'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('writeup_posts', 'last_fetched')
    op.drop_column('writeup_posts', 'url')


def downgrade():
    op.add_column('writeup_posts', sa.Column('url', sa.VARCHAR()))
    op.add_column('writeup_posts', sa.Column('last_fetched', postgresql.TIMESTAMP(timezone=True)))
