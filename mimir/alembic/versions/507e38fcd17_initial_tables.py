"""Initial tables

Revision ID: 507e38fcd17
Revises:
Create Date: 2015-07-05 01:07:23.508574

"""


from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from mimir import models

# revision identifiers, used by Alembic.
revision = '507e38fcd17'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'credentials',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=True),
        sa.Column('cookies', postgresql.JSONB(), nullable=False),
        sa.Column('timezone', sa.String(length=32), nullable=False),
        sa.Column('valid', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username')
    )
    op.create_table(
        'images',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('size', postgresql.ARRAY(sa.Integer()), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'threads',
        # TODO: prevent a sequence from being made for this
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('closed', sa.Boolean(), nullable=False),
        sa.Column('page_count', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'writeups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('author_slug', sa.String(length=100), nullable=False),
        sa.Column('writeup_slug', sa.String(length=100), nullable=False),
        sa.Column('title', sa.Unicode(length=100), nullable=False),
        sa.Column('status', sa.Enum('ongoing', 'abandoned', 'completed', native_enum=False), nullable=False),
        sa.Column('published', sa.Boolean(), nullable=False),
        sa.Column('offensive_content', sa.Boolean(), nullable=False),
        sa.Column('triggery_content', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('author_slug', 'writeup_slug')
    )
    op.create_index(op.f('ix_writeups_author_slug'), 'writeups', ['author_slug'], unique=False)
    op.create_index(op.f('ix_writeups_writeup_slug'), 'writeups', ['writeup_slug'], unique=False)
    op.create_table(
        'thread_pages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('thread_id', sa.Integer(), nullable=False),
        sa.Column('page_num', sa.Integer(), nullable=False),
        sa.Column('html', sa.UnicodeText(), nullable=False),
        sa.Column('last_fetched', models.AwareDateTime(), nullable=False),
        sa.Column('last_split', models.AwareDateTime(), nullable=True),
        sa.Column('fetched_with_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['fetched_with_id'], ['credentials.id'], ),
        sa.ForeignKeyConstraint(['thread_id'], ['threads.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('thread_id', 'page_num')
    )
    op.create_table(
        'writeup_posts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('writeup_id', sa.Integer(), nullable=False),
        sa.Column('author', sa.Unicode(length=40), nullable=False),
        sa.Column('index', sa.Integer(), nullable=False),
        sa.Column('ordinal', sa.Unicode(length=5), nullable=False),
        sa.Column('title', sa.Unicode(), nullable=True),
        sa.Column('url', sa.Unicode(), nullable=False),
        sa.Column('last_fetched', models.AwareDateTime(), nullable=False),
        sa.ForeignKeyConstraint(['writeup_id'], ['writeups.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'thread_posts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('thread_id', sa.Integer(), nullable=False),
        sa.Column('page_id', sa.Integer(), nullable=False),
        sa.Column('author', sa.Unicode(length=40), nullable=False),
        sa.Column('timestamp', models.AwareDateTime(), nullable=False),
        sa.Column('html', sa.UnicodeText(), nullable=False),
        sa.Column('last_extracted', models.AwareDateTime(), nullable=False),
        sa.ForeignKeyConstraint(['page_id'], ['thread_pages.id'], ),
        sa.ForeignKeyConstraint(['thread_id'], ['threads.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'writeup_post_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('writeuppost_id', sa.Integer(), nullable=False),
        sa.Column('html', sa.UnicodeText(), nullable=False),
        sa.Column('threadpost_id', sa.Integer(), nullable=True),
        sa.Column('extracted_at', models.AwareDateTime(), nullable=False),
        sa.ForeignKeyConstraint(['threadpost_id'], ['thread_posts.id'], ),
        sa.ForeignKeyConstraint(['writeuppost_id'], ['writeup_posts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('writeup_post_versions')
    op.drop_table('thread_posts')
    op.drop_table('writeup_posts')
    op.drop_table('thread_pages')
    op.drop_table('writeups')
    op.drop_table('threads')
    op.drop_table('images')
    op.drop_table('credentials')
