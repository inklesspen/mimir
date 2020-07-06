"""adjustments

Revision ID: 4efa2946f5a
Revises: 4dbff7d28fd
Create Date: 2015-08-30 22:02:00.790640

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4efa2946f5a"
down_revision = "4dbff7d28fd"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "writeup_posts",
        sa.Column("published", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.add_column(
        "writeup_post_versions",
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.add_column(
        "writeup_post_versions",
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
    )
    op.alter_column("writeup_posts", "published", server_default=None)
    op.alter_column("writeup_post_versions", "active", server_default=None)
    op.alter_column("writeup_post_versions", "version", server_default=None)


def downgrade():
    op.drop_column("writeup_posts", "published")
    op.drop_column("writeup_post_versions", "version")
    op.drop_column("writeup_post_versions", "active")
