"""private messages

Revision ID: a37bcdc43968
Revises: fcd7857556e2
Create Date: 2024-03-21 14:25:57.779639

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a37bcdc43968'
down_revision = 'fcd7857556e2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_db', schema=None) as batch_op:
        batch_op.add_column(sa.Column('last_message_read_time', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_db', schema=None) as batch_op:
        batch_op.drop_column('last_message_read_time')

    # ### end Alembic commands ###
