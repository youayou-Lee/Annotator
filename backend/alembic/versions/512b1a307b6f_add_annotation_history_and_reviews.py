"""add_annotation_history_and_reviews

Revision ID: 512b1a307b6f
Revises: 7061060e68df
Create Date: 2025-05-17 16:08:15.822876

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '512b1a307b6f'
down_revision: Union[str, None] = '7061060e68df'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 创建 annotation_history 表
    op.create_table('annotation_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('annotation_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('content', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['annotation_id'], ['annotations.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_annotation_history_id'), 'annotation_history', ['id'], unique=False)
    
    # 创建 annotation_reviews 表 - 使用已存在的 annotationstatus 枚举类型
    op.create_table('annotation_reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('annotation_id', sa.Integer(), nullable=False),
        sa.Column('reviewer_id', sa.Integer(), nullable=False),
        sa.Column('status', postgresql.ENUM('PENDING', 'APPROVED', 'REJECTED', 'CONFLICT', name='annotationstatus', create_type=False), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['annotation_id'], ['annotations.id']),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_annotation_reviews_id'), 'annotation_reviews', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # 删除 annotation_reviews 表
    op.drop_index(op.f('ix_annotation_reviews_id'), table_name='annotation_reviews')
    op.drop_table('annotation_reviews')
    
    # 删除 annotation_history 表
    op.drop_index(op.f('ix_annotation_history_id'), table_name='annotation_history')
    op.drop_table('annotation_history')
