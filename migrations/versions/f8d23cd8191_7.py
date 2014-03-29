"""7

Revision ID: f8d23cd8191
Revises: 3d8eec94b9a9
Create Date: 2014-03-28 20:41:13.107796

"""

# revision identifiers, used by Alembic.
revision = 'f8d23cd8191'
down_revision = '3d8eec94b9a9'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('student_teacher_association_table',
    sa.Column('teacher_id', sa.Integer(), nullable=False),
    sa.Column('student_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['teacher_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('teacher_id', 'student_id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('student_teacher_association_table')
    ### end Alembic commands ###