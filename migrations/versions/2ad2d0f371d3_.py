"""empty message

Revision ID: 2ad2d0f371d3
Revises: 4b54b5da67d4
Create Date: 2016-06-22 14:11:20.144597

"""

# revision identifiers, used by Alembic.
revision = '2ad2d0f371d3'
down_revision = '5968a1fac1ed'

from alembic import op

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    ## commands auto generated by Alembic - please adjust! ###
    ## end Alembic commands ###
    op.alter_column(table_name='manufacturer', column_name='name', type_=postgresql.VARCHAR(255), nullable=False)

    op.add_column(
        'manufacturer'
        ,sa.Column('markings', sa.Unicode(255), nullable=True)
    )

    op.add_column(
        'manufacturer'
        ,sa.Column('location', sa.Unicode(255), nullable=True)
    )
    op.add_column(
        'manufacturer'
        ,sa.Column('description', sa.Unicode(2048), nullable=True)
    )


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    ##drop_column# end Alembic commands ###
    op.alter_column(table_name='manufacturer', column_name='name', type_=postgresql.VARCHAR(50), nullable=False)
    op.drop_column('manufacturer', 'markings')
    op.drop_column('manufacturer', 'location')
    op.drop_column('manufacturer', 'description')
