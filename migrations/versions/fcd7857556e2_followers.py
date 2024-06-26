"""followers

Revision ID: fcd7857556e2
Revises: 10a83fe2cdb2
Create Date: 2024-03-02 23:14:00.146729

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fcd7857556e2'
down_revision = '10a83fe2cdb2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('contact')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('contact',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('email', sa.VARCHAR(length=100), nullable=False),
    sa.Column('message', sa.VARCHAR(length=150), nullable=False),
    sa.PrimaryKeyConstraint('id', name='pk_contact'),
    sa.UniqueConstraint('email', name='uq_contact_email')
    )
    # ### end Alembic commands ###
