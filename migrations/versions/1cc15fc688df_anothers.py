"""anothers

Revision ID: 1cc15fc688df
Revises: ff90caf68d7
Create Date: 2014-03-25 23:44:40.637724

"""

# revision identifiers, used by Alembic.
revision = '1cc15fc688df'
down_revision = 'ff90caf68d7'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('linkedin_id', sa.String(length=100), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'linkedin_id')
    ### end Alembic commands ###
