"""Initial migration

Revision ID: ef704c6c413c
Revises: 
Create Date: 2024-02-27 20:59:13.075172

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ef704c6c413c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('blog_posts', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_blog_posts_title'), ['title'])

    with op.batch_alter_table('user_db', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_user_db_email'), ['email'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_db', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_user_db_email'), type_='unique')

    with op.batch_alter_table('blog_posts', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_blog_posts_title'), type_='unique')

    # ### end Alembic commands ###