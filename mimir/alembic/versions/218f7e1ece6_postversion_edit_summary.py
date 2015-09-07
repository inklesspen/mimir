"""postversion edit summary

Revision ID: 218f7e1ece6
Revises: 4efa2946f5a
Create Date: 2015-09-06 18:44:28.424410

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '218f7e1ece6'
down_revision = '4efa2946f5a'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('writeup_post_versions', sa.Column('edit_summary', sa.Unicode(length=200), nullable=True))
    from mimir.models import AwareDateTime
    t_wpv = sa.table(
        'writeup_post_versions',
        sa.column('edit_summary', sa.Unicode(200)),
        sa.column('extracted_at', AwareDateTime),
    )
    stmt = t_wpv.update().values(
        edit_summary="Extracted at " + sa.cast(t_wpv.c.extracted_at, sa.Unicode)
    )
    op.get_bind().execute(stmt)
    op.alter_column('writeup_post_versions', 'edit_summary', nullable=False)
    op.alter_column('writeup_post_versions', 'extracted_at', new_column_name='created_at')


def downgrade():
    op.drop_column('writeup_post_versions', 'edit_summary')
    op.alter_column('writeup_post_versions', 'created_at', new_column_name='extracted_at')
