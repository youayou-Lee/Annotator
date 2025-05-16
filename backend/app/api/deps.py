from typing import Generator, Optional
import os
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.config import settings
from app.models.user import User
from app.services.user import get_user_by_email, get_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/login", auto_error=False)

# 开发环境令牌
DEV_TOKEN = "dev_temp_token"
# 模拟用户ID (确保这是数据库中存在的用户ID)
DEV_USER_ID = 1

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

async def get_token_from_header(request: Request) -> Optional[str]:
    """从Authorization头或dev_token查询参数中获取token"""
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.replace("Bearer ", "")
    # 检查查询参数
    token = request.query_params.get("dev_token")
    if token:
        return token
    return None

async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme)
) -> User:
    # 如果oauth2_scheme未能提取token，尝试从自定义位置获取
    if not token:
        token = await get_token_from_header(request)
    
    # 检查是否在开发环境中
    is_dev_mode = os.environ.get("ENVIRONMENT", "").lower() == "development"
    
    # 在开发环境中提供更宽松的认证
    if is_dev_mode:
        # 如果使用开发令牌或没有提供令牌，返回默认用户
        if not token or token == DEV_TOKEN:
            # 获取开发用户
            dev_user = get_user(db, DEV_USER_ID)
            if dev_user:
                return dev_user
            # 如果开发用户不存在，创建一个模拟用户对象
            mock_user = User(id=DEV_USER_ID, 
                            email="dev@example.com", 
                            username="developer",
                            is_active=True,
                            is_superuser=True)
            return mock_user
    
    # 正常的令牌验证流程
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user 