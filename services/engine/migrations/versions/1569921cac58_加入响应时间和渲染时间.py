"""加入响应时间和渲染时间

Revision ID: 1569921cac58
Revises: b3bd5bc9e4e3
Create Date: 2021-04-07 17:11:13.336649

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '1569921cac58'
down_revision = 'b3bd5bc9e4e3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('results', sa.Column('load_complete_time', sa.Integer(), nullable=True))
    op.add_column('results', sa.Column('response_time', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('results', 'response_time')
    op.drop_column('results', 'load_complete_time')
    # ### end Alembic commands ###
