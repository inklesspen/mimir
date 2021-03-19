"""Add indexes for costly queries

Revision ID: 80e1d61fc5ca
Revises: 02f4c870361c
Create Date: 2021-03-19 00:28:55.009950

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "80e1d61fc5ca"
down_revision = "02f4c870361c"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(op.f("ix_writeups_status"), "writeups", ["status"], unique=False)
    op.create_index(
        op.f("ix_writeups_collated_title"),
        "writeups",
        [sa.text('title COLLATE "writeuptitle"')],
        unique=False,
    )
    op.create_index(
        op.f("ix_writeup_posts_author"), "writeup_posts", ["author"], unique=False
    )
    op.create_index(
        op.f("ix_writeup_post_versions_writeuppost_id"),
        "writeup_post_versions",
        ["writeuppost_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_writeup_post_versions_unattached_wpv"),
        "writeup_post_versions",
        ["id"],
        unique=False,
        postgresql_where=sa.column("writeuppost_id") == sa.null(),
    )


def downgrade():
    op.drop_index(op.f("ix_writeups_status"), table_name="writeups")
    op.drop_index(op.f("ix_writeups_collated_title"), table_name="writeups")
    op.drop_index(op.f("ix_writeup_posts_author"), table_name="writeup_posts")
    op.drop_index(
        op.f("ix_writeup_post_versions_writeuppost_id"),
        table_name="writeup_post_versions",
    )
    op.drop_index(
        op.f("ix_writeup_post_versions_unattached_wpv"),
        table_name="writeup_post_versions",
    )
