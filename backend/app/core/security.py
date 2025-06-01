from datetime import datetime, timedelta
from typing import Optional, List, Callable
from functools import wraps
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..config import settings
from ..models.auth import TokenData
from ..models.user import UserInDB, UserRole
from .storage import StorageManager

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Bearer认证
security = HTTPBearer()

# 存储管理器
storage = StorageManager()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def verify_token(token: str) -> TokenData:
    """验证令牌"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证凭据",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = TokenData(username=username, user_id=user_id)
        return token_data
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserInDB:
    """获取当前用户"""
    token_data = verify_token(credentials.credentials)
    user = storage.get_user_by_id(token_data.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """获取当前活跃用户"""
    return current_user


def require_roles(allowed_roles: List[UserRole]):
    """
    权限控制装饰器，要求用户具有指定角色之一
    
    Args:
        allowed_roles: 允许的角色列表
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从kwargs中获取current_user参数
            current_user = kwargs.get('current_user')
            if not current_user:
                # 如果没有current_user参数，尝试从args中获取
                for arg in args:
                    if isinstance(arg, UserInDB):
                        current_user = arg
                        break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="需要认证"
                )
            
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="权限不足"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_admin():
    """要求管理员权限的装饰器"""
    return require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN])


def require_super_admin():
    """要求超级管理员权限的装饰器"""
    return require_roles([UserRole.SUPER_ADMIN])


def check_permission(current_user: UserInDB, required_roles: List[UserRole]):
    """检查用户权限"""
    if current_user.role not in required_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )


def check_admin_permission(current_user: UserInDB):
    """检查管理员权限"""
    check_permission(current_user, [UserRole.ADMIN, UserRole.SUPER_ADMIN])


def check_super_admin_permission(current_user: UserInDB):
    """检查超级管理员权限"""
    check_permission(current_user, [UserRole.SUPER_ADMIN])


def can_access_user(current_user: UserInDB, target_user_id: str) -> bool:
    """检查是否可以访问指定用户的信息"""
    # 用户可以访问自己的信息，或者管理员可以访问所有用户信息
    return (current_user.id == target_user_id or 
            current_user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN])


def can_modify_user(current_user: UserInDB, target_user_id: str) -> bool:
    """检查是否可以修改指定用户的信息"""
    # 用户可以修改自己的信息，或者管理员可以修改所有用户信息
    return (current_user.id == target_user_id or 
            current_user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN])


def can_assign_role(current_user: UserInDB, target_role: UserRole) -> bool:
    """检查是否可以分配指定角色"""
    # 只有超级管理员可以分配角色
    return current_user.role == UserRole.SUPER_ADMIN


def validate_password_strength(password: str) -> bool:
    """验证密码强度"""
    if len(password) < 6:
        return False
    # 可以添加更多密码强度验证规则
    return True


def create_initial_admin():
    """创建初始管理员账户"""
    try:
        # 检查是否已存在管理员账户
        existing_admin = storage.get_user_by_username("admin")
        if existing_admin:
            print("管理员账户已存在")
            return existing_admin
        
        # 创建初始管理员账户
        from ..models.user import UserCreate
        admin_user = UserCreate(
            username="admin",
            password="admin123",
            role=UserRole.SUPER_ADMIN
        )
        
        password_hash = get_password_hash("admin123")
        new_admin = storage.create_user(admin_user, password_hash)
        
        print(f"初始管理员账户创建成功:")
        print(f"用户名: admin")
        print(f"密码: admin123")
        print(f"角色: {new_admin.role}")
        print(f"请在生产环境中立即修改默认密码!")
        
        return new_admin
        
    except Exception as e:
        print(f"创建初始管理员账户失败: {e}")
        return None 