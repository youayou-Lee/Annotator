from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from ..models.user import User, UserUpdate, UserInDB, UserRole
from ..core.security import (
    get_current_user, get_password_hash, check_admin_permission,
    check_super_admin_permission, can_access_user, can_modify_user,
    can_assign_role, validate_password_strength
)
from ..core.storage import StorageManager

router = APIRouter()
storage = StorageManager()


@router.get("/", response_model=List[User], summary="获取用户列表")
async def get_users(current_user: UserInDB = Depends(get_current_user)):
    """获取用户列表（需要管理员权限）"""
    check_admin_permission(current_user)
    
    try:
        users = storage.get_all_users()
        return [
            User(
                id=user.id,
                username=user.username,
                role=user.role,
                created_at=user.created_at
            ) for user in users
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户列表失败: {str(e)}"
        )


@router.get("/{user_id}", response_model=User, summary="获取用户详情")
async def get_user(user_id: str, current_user: UserInDB = Depends(get_current_user)):
    """获取用户详情"""
    # 检查访问权限
    if not can_access_user(current_user, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，只能查看自己的信息"
        )
    
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
    # 检查修改权限
    if not can_modify_user(current_user, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，只能修改自己的信息"
        )
    
    user = storage.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 准备更新数据
    update_data = {}
    
    # 更新用户名
    if user_update.username is not None:
        # 验证用户名格式
        import re
        if not re.match(r'^[a-zA-Z0-9_]+$', user_update.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名只能包含字母、数字和下划线"
            )
        
        # 验证用户名长度
        if len(user_update.username) < 3 or len(user_update.username) > 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名长度必须在3-20个字符之间"
            )
        
        # 检查用户名是否已存在
        existing_user = storage.get_user_by_username(user_update.username)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        update_data["username"] = user_update.username
    
    # 更新密码
    if user_update.password is not None:
        # 验证密码强度
        if not validate_password_strength(user_update.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="密码长度至少6个字符"
            )
        update_data["password_hash"] = get_password_hash(user_update.password)
    
    # 更新角色
    if user_update.role is not None:
        # 检查角色分配权限
        if not can_assign_role(current_user, user_update.role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有超级管理员可以修改用户角色"
            )
        
        # 防止用户修改自己的角色为更低权限
        if current_user.id == user_id and user_update.role != current_user.role:
            if current_user.role == UserRole.SUPER_ADMIN:
                # 检查是否还有其他超级管理员
                all_users = storage.get_all_users()
                super_admins = [u for u in all_users if u.role == UserRole.SUPER_ADMIN and u.id != user_id]
                if not super_admins:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="不能删除最后一个超级管理员"
                    )
        
        update_data["role"] = user_update.role
    
    # 更新用户
    try:
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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新用户失败: {str(e)}"
        )


@router.delete("/{user_id}", summary="删除用户")
async def delete_user(
    user_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """删除用户（需要超级管理员权限）"""
    check_super_admin_permission(current_user)
    
    # 不能删除自己
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账户"
        )
    
    user = storage.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 如果要删除的是超级管理员，检查是否还有其他超级管理员
    if user.role == UserRole.SUPER_ADMIN:
        all_users = storage.get_all_users()
        super_admins = [u for u in all_users if u.role == UserRole.SUPER_ADMIN and u.id != user_id]
        if not super_admins:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能删除最后一个超级管理员"
            )
    
    try:
        # 删除用户
        success = storage.delete_user(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="删除用户失败"
            )
        
        return {"message": f"用户 {user.username} 删除成功"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除用户失败: {str(e)}"
        ) 