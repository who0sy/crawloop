"""记录cookies

Revision ID: 81a88acb3641
Revises: 8efa2b9dcc87
Create Date: 2020-12-22 15:37:26.700404

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '81a88acb3641'
down_revision = '8efa2b9dcc87'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('results', sa.Column('cookies', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('results', 'cookies')
    # ### end Alembic commands ###
