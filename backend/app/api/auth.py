from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from ..models.auth import Token, LoginRequest, RegisterRequest
from ..models.user import User, UserCreate, UserInDB
from ..core.security import (
    verify_password, get_password_hash, create_access_token, 
    get_current_user
)
from ..core.storage import StorageManager
from ..config import settings

router = APIRouter()
storage = StorageManager()
security = HTTPBearer()


@router.post("/login", response_model=Token, summary="用户登录")
async def login(login_data: LoginRequest):
    """用户登录接口"""
    # 验证用户
    user = storage.get_user_by_username(login_data.username)
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=User, summary="用户注册")
async def register(register_data: RegisterRequest):
    """用户注册接口"""
    # 检查用户名是否已存在
    existing_user = storage.get_user_by_username(register_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 创建新用户
    user_create = UserCreate(
        username=register_data.username,
        password=register_data.password,
        role=register_data.role
    )
    
    password_hash = get_password_hash(register_data.password)
    new_user = storage.create_user(user_create, password_hash)
    
    return User(
        id=new_user.id,
        username=new_user.username,
        role=new_user.role,
        created_at=new_user.created_at
    )


@router.get("/me", response_model=User, summary="获取当前用户信息")
async def get_current_user_info(current_user: UserInDB = Depends(get_current_user)):
    """获取当前用户信息"""
    return User(
        id=current_user.id,
        username=current_user.username,
        role=current_user.role,
        created_at=current_user.created_at
    ) 