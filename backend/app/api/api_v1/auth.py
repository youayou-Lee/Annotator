from datetime import timedelta
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, get_current_user
from app.db.session import get_db
from app.models.user import UserRole, UserStatus, User as DBUser
from app.schemas.user import User, UserCreate, ApprovalRequest, UserWithApprovedUsers
from app.services.user import (
    authenticate_user, create_user, get_user_by_email, get_superuser,
    get_pending_admins, approve_user
)

router = APIRouter()

@router.post("/login", response_model=dict)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 兼容的令牌登录，获取访问令牌
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user.email}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/register", response_model=User)
def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate
) -> Any:
    """
    注册新用户
    """
    user = get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册"
        )
    
    # 检查超级管理员权限
    if user_in.role == UserRole.superuser:
        # 检查系统中是否已存在超级管理员
        superuser = get_superuser(db)
        if superuser:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="系统中已存在超级管理员"
            )
    
    user = create_user(db, user_in)
    return user

@router.get("/pending-admins", response_model=List[User])
def get_pending_admin_users(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    获取待审批的管理员用户列表（仅超级管理员可访问）
    """
    if current_user.role != UserRole.superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限访问此资源"
        )
    
    return get_pending_admins(db, skip=skip, limit=limit)

@router.post("/approve", response_model=User)
def approve_admin_user(
    *,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
    approval: ApprovalRequest
) -> Any:
    """
    批准或拒绝管理员用户的注册请求（仅超级管理员可访问）
    """
    if current_user.role != UserRole.superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有超级管理员可以批准管理员注册"
        )
    
    updated_user = approve_user(db, approval, current_user.id)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到指定用户"
        )
    
    return updated_user

@router.get("/me", response_model=User)
def read_users_me(
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    获取当前登录用户信息
    """
    return current_user

@router.get("/superuser-info", response_model=UserWithApprovedUsers)
def get_superuser_info(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user)
) -> Any:
    """
    获取超级管理员信息及其批准的用户（仅超级管理员可访问）
    """
    if current_user.role != UserRole.superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有超级管理员可以访问此资源"
        )
    
    return current_user 