from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from ..models.auth import Token, LoginRequest, RegisterRequest, ChangePasswordRequest
from ..models.user import User, UserCreate, UserInDB, UserRole
from ..core.security import (
    verify_password, get_password_hash, create_access_token, 
    get_current_user, validate_password_strength
)
from ..core.storage import StorageManager
from ..config import settings

router = APIRouter()
storage = StorageManager()
security = HTTPBearer()


@router.post("/login", response_model=Token, summary="用户登录")
async def login(login_data: LoginRequest):
    """
    用户登录接口
    
    - **username**: 用户名
    - **password**: 密码
    
    返回JWT访问令牌
    """
    # 输入验证
    if not login_data.username or not login_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名和密码不能为空"
        )
    
    # 验证用户
    user = storage.get_user_by_username(login_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={
            "sub": user.username, 
            "user_id": user.id,
            "role": user.role
        },
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }
    }


@router.post("/register", response_model=User, summary="用户注册")
async def register(register_data: RegisterRequest):
    """
    用户注册接口
    
    - **username**: 用户名（3-20个字符）
    - **password**: 密码（至少6个字符）
    - **role**: 用户角色（默认为annotator）
    
    注意：只有管理员可以注册admin和super_admin角色的用户
    """
    # 输入验证
    if not register_data.username or not register_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名和密码不能为空"
        )
    
    # 用户名长度验证
    if len(register_data.username) < 3 or len(register_data.username) > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名长度必须在3-20个字符之间"
        )
    
    # 用户名格式验证（只允许字母、数字、下划线）
    import re
    if not re.match(r'^[a-zA-Z0-9_]+$', register_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名只能包含字母、数字和下划线"
        )
    
    # 密码强度验证
    if not validate_password_strength(register_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码长度至少6个字符"
        )
    
    # 角色验证
    try:
        role = UserRole(register_data.role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的用户角色"
        )
    
    # 检查是否允许注册管理员角色
    if role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        # 检查是否已有管理员用户，如果没有则允许创建第一个管理员
        all_users = storage.get_all_users()
        has_admin = any(user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN] for user in all_users)
        
        if has_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有现有管理员可以创建新的管理员账户"
            )
    
    # 检查用户名是否已存在
    existing_user = storage.get_user_by_username(register_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 创建新用户
    try:
        user_create = UserCreate(
            username=register_data.username,
            password=register_data.password,
            role=role
        )
        
        password_hash = get_password_hash(register_data.password)
        new_user = storage.create_user(user_create, password_hash)
        
        return User(
            id=new_user.id,
            username=new_user.username,
            role=new_user.role,
            created_at=new_user.created_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建用户失败: {str(e)}"
        )


@router.get("/me", response_model=User, summary="获取当前用户信息")
async def get_current_user_info(current_user: UserInDB = Depends(get_current_user)):
    """
    获取当前登录用户的信息
    
    需要有效的JWT令牌
    """
    return User(
        id=current_user.id,
        username=current_user.username,
        role=current_user.role,
        created_at=current_user.created_at
    )


@router.post("/refresh", response_model=Token, summary="刷新访问令牌")
async def refresh_token(current_user: UserInDB = Depends(get_current_user)):
    """
    刷新访问令牌
    
    使用当前有效的令牌获取新的令牌
    """
    # 创建新的访问令牌
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={
            "sub": current_user.username, 
            "user_id": current_user.id,
            "role": current_user.role
        },
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60
    }


@router.post("/change-password", summary="修改密码")
async def change_password(
    request: ChangePasswordRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    修改当前用户密码
    
    - **old_password**: 当前密码
    - **new_password**: 新密码
    """
    # 验证当前密码
    if not verify_password(request.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前密码错误"
        )
    
    # 验证新密码强度
    if not validate_password_strength(request.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码长度至少6个字符"
        )
    
    # 检查新密码是否与旧密码相同
    if request.old_password == request.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码不能与当前密码相同"
        )
    
    # 更新密码
    try:
        new_password_hash = get_password_hash(request.new_password)
        storage.update_user(current_user.id, {"password_hash": new_password_hash})
        
        return {"message": "密码修改成功"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"修改密码失败: {str(e)}"
        ) 