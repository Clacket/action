"""empty message

Revision ID: b7652c4a9a92
Revises: 62c7982b2667
Create Date: 2017-10-20 18:01:47.338649

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b7652c4a9a92'
down_revision = '62c7982b2667'
branch_labels = None
depends_on = None


def upgrade(engine_name):
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name):
    globals()["downgrade_%s" % engine_name]()


def upgrade_():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        'movie', sa.Column('description', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade_():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('movie', 'description')
    # ### end Alembic commands ###


def upgrade_admin():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade_admin():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###