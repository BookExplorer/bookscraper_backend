"""Add columns to author table

Revision ID: 6cabf02789e2
Revises: e216d7ecdc8c
Create Date: 2024-02-28 20:55:43.935134

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6cabf02789e2'
down_revision: Union[str, None] = 'e216d7ecdc8c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('authors', sa.Column('gr_link', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('authors', 'gr_link')
    # ### end Alembic commands ###
