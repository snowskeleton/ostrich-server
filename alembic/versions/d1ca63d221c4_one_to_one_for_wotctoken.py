"""one to one for wotcToken

Revision ID: d1ca63d221c4
Revises: e31a0bdd7dc0
Create Date: 2024-05-16 21:48:22.797343

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1ca63d221c4'
down_revision: Union[str, None] = 'e31a0bdd7dc0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
