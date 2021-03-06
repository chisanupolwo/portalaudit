"""initial migration

Revision ID: 70d1693f9abb
Revises: a40fdf993a0c
Create Date: 2020-05-27 00:29:30.896012

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '70d1693f9abb'
down_revision = 'a40fdf993a0c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comments', sa.Column('job', sa.String(length=32), nullable=True))
    op.create_index(op.f('ix_comments_job'), 'comments', ['job'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_comments_job'), table_name='comments')
    op.drop_column('comments', 'job')
    # ### end Alembic commands ###
