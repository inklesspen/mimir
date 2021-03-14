"""trim whitespace from titles

Revision ID: 02f4c870361c
Revises: 44ff152e0a7c
Create Date: 2021-03-13 18:04:31.541185

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "02f4c870361c"
down_revision = "44ff152e0a7c"
branch_labels = None
depends_on = None


writeups = sa.table("writeups", sa.column("title", sa.String))
writeup_posts = sa.table("writeup_posts", sa.column("title", sa.String))


def upgrade():
    op.execute(
        writeups.update()
        .where(sa.or_(writeups.c.title.startswith(" "), writeups.c.title.endswith(" ")))
        .values(title=sa.func.trim(writeups.c.title))
    )

    op.execute(
        writeup_posts.update()
        .where(
            sa.or_(
                writeup_posts.c.title.startswith(" "),
                writeup_posts.c.title.endswith(" "),
            )
        )
        .values(title=sa.func.trim(writeup_posts.c.title))
    )


def downgrade():
    pass
