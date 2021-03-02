"""starting prod schema

Revision ID: 41d36feab50
Create Date: 2020-11-22 08:55:52.116481

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from mimir import models


# revision identifiers, used by Alembic.
revision = "41d36feab50"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "authorized_users",
        sa.Column(
            "id",
            sa.INTEGER(),
            primary_key=True,
        ),
        sa.Column("email", sa.VARCHAR(length=255), nullable=False),
        sa.Column("name", sa.VARCHAR(), nullable=False),
        sa.UniqueConstraint("email", name=op.f("uq_authorized_users_email")),
    )
    op.create_table(
        "credentials",
        sa.Column(
            "id",
            sa.INTEGER(),
            primary_key=True,
        ),
        sa.Column("username", sa.VARCHAR(length=100), nullable=True, unique=True),
        sa.Column(
            "cookies",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("timezone", sa.VARCHAR(length=32), nullable=False),
        sa.Column("valid", sa.BOOLEAN(), nullable=False),
    )
    op.create_table(
        "fetched_images",
        sa.Column("orig_url", sa.VARCHAR(), primary_key=True),
        sa.Column("id", sa.VARCHAR(length=64), nullable=False),
    )
    op.create_table(
        "threads",
        sa.Column(
            "id",
            sa.INTEGER(),
            primary_key=True,
            autoincrement=False,
        ),
        sa.Column("closed", sa.BOOLEAN(), nullable=False),
        sa.Column("page_count", sa.INTEGER(), nullable=False),
    )
    op.create_table(
        "writeups",
        sa.Column(
            "id",
            sa.INTEGER(),
            primary_key=True,
        ),
        sa.Column("author_slug", sa.VARCHAR(length=100), nullable=False, index=True),
        sa.Column("writeup_slug", sa.VARCHAR(length=100), nullable=False, index=True),
        sa.Column("title", sa.VARCHAR(length=100), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "ongoing",
                "abandoned",
                "completed",
                name=op.f("ck_writeups_check_status"),
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("published", sa.BOOLEAN(), nullable=False),
        sa.Column("offensive_content", sa.BOOLEAN(), nullable=False),
        sa.Column("triggery_content", sa.BOOLEAN(), nullable=False),
        sa.Column("author", sa.VARCHAR(length=100), nullable=False),
        sa.UniqueConstraint(
            "author_slug",
            "writeup_slug",
            name=op.f("uq_writeups_author_slug_writeup_slug"),
        ),
    )
    op.create_table(
        "audit_entries",
        sa.Column(
            "id",
            sa.INTEGER(),
            primary_key=True,
        ),
        sa.Column("text", sa.VARCHAR(), nullable=False),
        sa.Column("timestamp", models.column_types.AwareDateTime(), nullable=False),
        sa.Column("user_id", sa.INTEGER(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["authorized_users.id"],
            name=op.f("fk_audit_entries_user_id_authorized_users"),
        ),
    )
    op.create_table(
        "thread_pages",
        sa.Column(
            "id",
            sa.INTEGER(),
            primary_key=True,
        ),
        sa.Column("thread_id", sa.INTEGER(), nullable=False),
        sa.Column("page_num", sa.INTEGER(), nullable=False),
        sa.Column("html", sa.TEXT(), nullable=False),
        sa.Column("last_fetched", models.column_types.AwareDateTime(), nullable=False),
        sa.Column("last_split", models.column_types.AwareDateTime(), nullable=True),
        sa.Column("fetched_with_id", sa.INTEGER(), nullable=False),
        sa.ForeignKeyConstraint(
            ["fetched_with_id"],
            ["credentials.id"],
            name=op.f("fk_thread_pages_fetched_with_id_credentials"),
        ),
        sa.ForeignKeyConstraint(
            ["thread_id"],
            ["threads.id"],
            name=op.f("fk_thread_pages_thread_id_threads"),
        ),
        sa.UniqueConstraint(
            "thread_id", "page_num", name=op.f("uq_thread_pages_thread_id_page_num")
        ),
    )
    op.create_table(
        "writeup_posts",
        sa.Column(
            "id",
            sa.INTEGER(),
            primary_key=True,
        ),
        sa.Column("writeup_id", sa.INTEGER(), nullable=False),
        sa.Column("author", sa.VARCHAR(length=40), nullable=False),
        sa.Column("index", sa.INTEGER(), nullable=False),
        sa.Column("ordinal", sa.VARCHAR(length=5), nullable=False),
        sa.Column("title", sa.VARCHAR(), nullable=True),
        sa.Column("published", sa.BOOLEAN(), nullable=False),
        sa.ForeignKeyConstraint(
            ["writeup_id"],
            ["writeups.id"],
            name=op.f("fk_writeup_posts_writeup_id_writeups"),
        ),
    )
    op.create_table(
        "thread_posts",
        sa.Column("id", sa.INTEGER(), primary_key=True, autoincrement=False),
        sa.Column("thread_id", sa.INTEGER(), nullable=False),
        sa.Column("page_id", sa.INTEGER(), nullable=False),
        sa.Column("author", sa.VARCHAR(length=40), nullable=False),
        sa.Column("timestamp", models.column_types.AwareDateTime(), nullable=False),
        sa.Column("html", sa.TEXT(), nullable=False),
        sa.Column(
            "last_extracted", models.column_types.AwareDateTime(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["page_id"],
            ["thread_pages.id"],
            name=op.f("fk_thread_posts_page_id_thread_pages"),
        ),
        sa.ForeignKeyConstraint(
            ["thread_id"],
            ["threads.id"],
            name=op.f("fk_thread_posts_thread_id_threads"),
        ),
    )
    op.create_table(
        "writeup_post_versions",
        sa.Column(
            "id",
            sa.INTEGER(),
            primary_key=True,
        ),
        sa.Column("writeuppost_id", sa.INTEGER(), nullable=True),
        sa.Column("html", sa.TEXT(), nullable=True),
        sa.Column("threadpost_id", sa.INTEGER(), nullable=False),
        sa.Column("created_at", models.column_types.AwareDateTime(), nullable=False),
        sa.Column("active", sa.BOOLEAN(), nullable=False),
        sa.Column("version", sa.INTEGER(), nullable=False),
        sa.Column("edit_summary", sa.VARCHAR(length=200), nullable=False),
        sa.CheckConstraint(
            "(writeuppost_id IS NOT NULL) OR (active = false)",
            name=op.f("ck_writeup_post_versions_check_attachment"),
        ),
        sa.ForeignKeyConstraint(
            ["threadpost_id"],
            ["thread_posts.id"],
            name=op.f("fk_writeup_post_versions_threadpost_id_thread_posts"),
        ),
        sa.ForeignKeyConstraint(
            ["writeuppost_id"],
            ["writeup_posts.id"],
            name=op.f("fk_writeup_post_versions_writeuppost_id_writeup_posts"),
        ),
    )


def downgrade():
    op.drop_table("writeup_post_versions")
    op.drop_table("thread_posts")
    op.drop_table("writeup_posts")
    op.drop_table("thread_pages")
    op.drop_table("audit_entries")
    op.drop_table("writeups")
    op.drop_table("threads")
    op.drop_table("fetched_images")
    op.drop_table("credentials")
    op.drop_table("authorized_users")
