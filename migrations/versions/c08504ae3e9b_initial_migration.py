"""initial migration

Revision ID: c08504ae3e9b
Revises: a84b9f231758
Create Date: 2020-05-23 01:32:06.991732

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c08504ae3e9b'
down_revision = 'a84b9f231758'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shipments', sa.Column('ata', sa.DateTime(), nullable=True))
    op.add_column('shipments', sa.Column('atd', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('shipments', 'atd')
    op.drop_column('shipments', 'ata')
    # ### end Alembic commands ###
