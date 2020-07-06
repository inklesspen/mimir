"""WPV nulls

Revision ID: 2b489140be5
Revises: 218f7e1ece6
Create Date: 2015-10-26 02:22:23.844785

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2b489140be5"
down_revision = "218f7e1ece6"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("writeup_post_versions", "threadpost_id", nullable=False)
    op.alter_column("writeup_post_versions", "writeuppost_id", nullable=True)
    op.alter_column("writeup_post_versions", "html", nullable=True)
    op.create_check_constraint(
        "writeup_post_versions_check_html",
        "writeup_post_versions",
        sa.and_(
            sa.column("writeuppost_id") != sa.null(), sa.column("html") != sa.null()
        ),
    )


def downgrade():
    op.alter_column("writeup_post_versions", "writeuppost_id", nullable=False)
    op.alter_column("writeup_post_versions", "threadpost_id", nullable=True)
    op.alter_column("writeup_post_versions", "html", nullable=False)
    op.drop_constraint("writeup_post_versions_check_html", "writeup_post_versions")
