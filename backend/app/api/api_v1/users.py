from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User as DBUser, UserRole, UserStatus
from app.schemas.user import User, UserCreate, UserUpdate
from app.core.security import get_current_user
from app.services.user import (
    get_user,
    get_users,
    create_user,
    update_user,
    delete_user,
    get_user_by_email,
    get_users_by_role
)

router = APIRouter()

@router.get("/", response_model=List[User])
def read_users(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    获取用户列表（需要管理员或超级管理员权限）
    """
    if current_user.role not in [UserRole.admin, UserRole.superuser]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限访问此资源"
        )
    users = get_users(db, skip=skip, limit=limit)
    return users

@router.get("/by-role/{role}", response_model=List[User])
def read_users_by_role(
    *,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
    role: UserRole,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    通过角色获取用户列表（需要管理员或超级管理员权限）
    """
    if current_user.role not in [UserRole.admin, UserRole.superuser]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限访问此资源"
        )
    users = get_users_by_role(db, role=role, skip=skip, limit=limit)
    return users

@router.post("/", response_model=User)
def create_new_user(
    *,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
    user_in: UserCreate
) -> Any:
    """
    创建新用户（需要管理员或超级管理员权限）
    """
    # 检查权限
    if current_user.role not in [UserRole.admin, UserRole.superuser]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限执行此操作"
        )
    
    # 检查创建的用户角色
    if user_in.role == UserRole.superuser and current_user.role != UserRole.superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有超级管理员可以创建其他超级管理员"
        )
    
    # 检查邮箱是否已存在
    existing_user = get_user_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册"
        )
    
    user = create_user(db, user_in)
    return user

@router.get("/{user_id}", response_model=User)
def read_user(
    *,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
    user_id: int,
) -> Any:
    """
    通过ID获取用户
    """
    # 普通用户只能查看自己
    if current_user.role == UserRole.annotator and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限访问此资源"
        )
    
    user = get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return user

@router.put("/{user_id}", response_model=User)
def update_user_info(
    *,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
    user_id: int,
    user_in: UserUpdate
) -> Any:
    """
    更新用户
    """
    user = get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 权限检查
    if current_user.id != user_id and current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能修改自己的信息或需要管理员权限"
        )
    
    # 管理员不能修改超级管理员
    if user.role == UserRole.SUPERUSER and current_user.role != UserRole.SUPERUSER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有超级管理员可以修改超级管理员信息"
        )
    
    # 不允许普通用户修改自己的角色
    if "role" in user_in.model_dump(exclude_unset=True) and current_user.role == UserRole.ANNOTATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无法修改用户角色"
        )
    
    updated_user = update_user(db, user_id=user_id, user=user_in)
    return updated_user

@router.delete("/{user_id}", response_model=User)
def delete_user_account(
    *,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
    user_id: int,
) -> Any:
    """
    删除用户（需要超级管理员权限）
    """
    if current_user.role != UserRole.SUPERUSER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有超级管理员可以删除用户"
        )
    
    user = get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 不允许删除最后一个超级管理员
    if user.role == UserRole.SUPERUSER:
        superusers = get_users_by_role(db, role=UserRole.SUPERUSER)
        if len(superusers) <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能删除系统中唯一的超级管理员"
            )
    
    deleted_user = delete_user(db, user_id=user_id)
    return deleted_user 