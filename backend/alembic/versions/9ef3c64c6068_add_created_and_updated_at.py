"""add_created_and_updated_at

Revision ID: 9ef3c64c6068
Revises: 512b1a307b6f
Create Date: 2025-05-17 16:48:53.052677

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime

# revision identifiers, used by Alembic.
revision: str = '9ef3c64c6068'
down_revision: Union[str, None] = '512b1a307b6f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 只添加新列，不删除表
    op.add_column('users', sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(), nullable=True))
    
    # 更新现有用户记录
    op.execute("UPDATE users SET created_at = NOW(), updated_at = NOW()")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'created_at')
