"""FetchedImage model

Revision ID: 3ffa3fb372a
Revises: 2b489140be5
Create Date: 2015-11-22 16:55:56.812428

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "3ffa3fb372a"
down_revision = "2b489140be5"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "fetched_images",
        sa.Column("orig_url", sa.String(), nullable=False),
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("orig_url"),
    )
    op.drop_table("images")


def downgrade():
    op.create_table(
        "images",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("size", postgresql.ARRAY(sa.Integer()), nullable=False),
        sa.PrimaryKeyConstraint("id", name="images_pkey"),
    )
    op.drop_table("fetched_images")
