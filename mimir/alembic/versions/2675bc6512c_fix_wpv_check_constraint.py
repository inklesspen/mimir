"""fix WPV check constraint

Revision ID: 2675bc6512c
Revises: 3ffa3fb372a
Create Date: 2015-11-29 05:26:00.735559

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2675bc6512c'
down_revision = '3ffa3fb372a'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('writeup_post_versions_check_html', 'writeup_post_versions')
    op.create_check_constraint(
        'writeup_post_versions_check_attachment', 'writeup_post_versions',
        sa.or_(sa.column('writeuppost_id') != sa.null(), sa.column('active') == sa.false()))


def downgrade():
    op.drop_constraint('writeup_post_versions_check_attachment', 'writeup_post_versions')
    op.create_check_constraint(
        'writeup_post_versions_check_html', 'writeup_post_versions',
        sa.and_(sa.column('writeuppost_id') != sa.null(), sa.column('html') != sa.null()))
