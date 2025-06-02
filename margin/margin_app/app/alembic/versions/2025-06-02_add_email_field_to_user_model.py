"""add email field to user model

Revision ID: 42d938760ce7
Revises: f7f3b6e10769
Create Date: 2025-06-02 10:39:38.603617

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '42d938760ce7'
down_revision: Union[str, None] = 'f7f3b6e10769'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Adds email field to user table with unique constraint.
    """
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column(
            'email', 
            sa.String(length=255), 
            nullable=True, 
            comment='The unique email address of the user.'
        ))
        batch_op.create_unique_constraint(None, ['email'])


def downgrade() -> None:
    """
    Removes email field and its constraints from user table.
    """
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_column('email')