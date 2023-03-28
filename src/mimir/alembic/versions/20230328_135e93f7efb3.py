"""threadpage utc offset

Revision ID: 135e93f7efb3
Revises: 80e1d61fc5ca
Create Date: 2023-03-28 15:14:37.397458

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "135e93f7efb3"
down_revision = "80e1d61fc5ca"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "thread_pages", sa.Column("utc_offset_at_fetch", sa.Integer(), nullable=True)
    )


def downgrade():
    op.drop_column("thread_pages", "utc_offset_at_fetch")
