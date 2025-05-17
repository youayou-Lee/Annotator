"""empty message

Revision ID: 5642ca1e7ec6
Revises: b882008d92fe, 4c891e5abc12
Create Date: 2025-05-17 16:07:44.319635

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5642ca1e7ec6'
down_revision: Union[str, None] = ('b882008d92fe', '4c891e5abc12')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
