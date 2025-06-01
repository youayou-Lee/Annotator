from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from ..models.user import User, UserUpdate, UserInDB, UserRole
from ..core.security import get_current_user, get_password_hash
from ..core.storage import StorageManager

router = APIRouter()
storage = StorageManager()


def check_admin_permission(current_user: UserInDB):
    """检查管理员权限"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )


@router.get("/", response_model=List[User], summary="获取用户列表")
async def get_users(current_user: UserInDB = Depends(get_current_user)):
    """获取用户列表（需要管理员权限）"""
    check_admin_permission(current_user)
    
    users = storage.get_all_users()
    return [
        User(
            id=user.id,
            username=user.username,
            role=user.role,
            created_at=user.created_at
        ) for user in users
    ]


@router.get("/{user_id}", response_model=User, summary="获取用户详情")
async def get_user(user_id: str, current_user: UserInDB = Depends(get_current_user)):
    """获取用户详情"""
    # 只能查看自己的信息或管理员可以查看所有用户
    if current_user.id != user_id:
        check_admin_permission(current_user)
    
    user = storage.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return User(
        id=user.id,
        username=user.username,
        role=user.role,
        created_at=user.created_at
    )


@router.put("/{user_id}", response_model=User, summary="更新用户信息")
async def update_user(
    user_id: str, 
    user_update: UserUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    """更新用户信息"""
    # 只能更新自己的信息或管理员可以更新所有用户
    if current_user.id != user_id:
        check_admin_permission(current_user)
    
    user = storage.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 准备更新数据
    update_data = {}
    if user_update.username is not None:
        # 检查用户名是否已存在
        existing_user = storage.get_user_by_username(user_update.username)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        update_data["username"] = user_update.username
    
    if user_update.password is not None:
        update_data["password_hash"] = get_password_hash(user_update.password)
    
    if user_update.role is not None:
        # 只有超级管理员可以修改角色
        if current_user.role != UserRole.SUPER_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有超级管理员可以修改用户角色"
            )
        update_data["role"] = user_update.role
    
    # 更新用户
    updated_user = storage.update_user(user_id, update_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新用户失败"
        )
    
    return User(
        id=updated_user.id,
        username=updated_user.username,
        role=updated_user.role,
        created_at=updated_user.created_at
    ) 