"""empty message

Revision ID: 3c75b70c61c4
Revises: 4a992d9d4aee
Create Date: 2023-12-24 18:01:06.675962

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3c75b70c61c4'
down_revision = '4a992d9d4aee'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Artist', schema=None) as batch_op:
        batch_op.add_column(sa.Column('website', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('seeking_venue', sa.BOOLEAN(), nullable=True))
        batch_op.add_column(sa.Column('seeking_description', sa.String(length=900), nullable=True))

    with op.batch_alter_table('Venue', schema=None) as batch_op:
        batch_op.add_column(sa.Column('genres', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('website', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('seeking_talent', sa.BOOLEAN(), nullable=True))
        batch_op.add_column(sa.Column('seeking_description', sa.String(length=900), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Venue', schema=None) as batch_op:
        batch_op.drop_column('seeking_description')
        batch_op.drop_column('seeking_talent')
        batch_op.drop_column('website')
        batch_op.drop_column('genres')

    with op.batch_alter_table('Artist', schema=None) as batch_op:
        batch_op.drop_column('seeking_description')
        batch_op.drop_column('seeking_venue')
        batch_op.drop_column('website')

    # ### end Alembic commands ###
