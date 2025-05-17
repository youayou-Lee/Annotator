"""user_role_and_approval

Revision ID: 4c891e5abc12
Revises: 2c839e7ddaa5
Create Date: 2024-06-20 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4c891e5abc12'
down_revision = '2c839e7ddaa5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建用户角色枚举类型
    op.execute(
        "CREATE TYPE userrole AS ENUM ('superuser', 'admin', 'annotator')"
    )
    
    # 创建用户状态枚举类型
    op.execute(
        "CREATE TYPE userstatus AS ENUM ('pending', 'approved', 'rejected')"
    )
    
    # 添加新字段到用户表
    op.add_column('users', sa.Column('role', sa.Enum('superuser', 'admin', 'annotator', name='userrole'), 
                                    nullable=False, server_default='annotator'))
    op.add_column('users', sa.Column('status', sa.Enum('pending', 'approved', 'rejected', name='userstatus'), 
                                    nullable=False, server_default='pending'))
    op.add_column('users', sa.Column('approval_date', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('approved_by_id', sa.Integer(), nullable=True))
    
    # 添加外键约束
    op.create_foreign_key(
        'fk_users_approved_by_id_users',
        'users', 'users',
        ['approved_by_id'], ['id']
    )
    
    # 将现有超级用户的状态设置为已批准
    op.execute(
        "UPDATE users SET status = 'approved' WHERE is_superuser = TRUE"
    )
    
    # 将现有超级用户的角色设置为superuser
    op.execute(
        "UPDATE users SET role = 'superuser' WHERE is_superuser = TRUE"
    )
    
    # 将所有其他现有用户的状态设置为已批准
    op.execute(
        "UPDATE users SET status = 'approved' WHERE is_superuser = FALSE"
    )


def downgrade() -> None:
    # 删除外键约束
    op.drop_constraint('fk_users_approved_by_id_users', 'users', type_='foreignkey')
    
    # 删除列
    op.drop_column('users', 'approved_by_id')
    op.drop_column('users', 'approval_date')
    op.drop_column('users', 'status')
    op.drop_column('users', 'role')
    
    # 删除枚举类型
    op.execute("DROP TYPE userstatus")
    op.execute("DROP TYPE userrole") 