from typing import Optional
from pydantic import BaseModel, Field, validator


class Token(BaseModel):
    """JWT令牌模型"""
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    user: Optional[dict] = None


class TokenData(BaseModel):
    """令牌数据模型"""
    username: Optional[str] = None
    user_id: Optional[str] = None
    role: Optional[str] = None


class LoginRequest(BaseModel):
    """登录请求模型"""
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    password: str = Field(..., min_length=1, description="密码")
    
    @validator('username')
    def username_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('用户名不能为空')
        return v.strip()
    
    @validator('password')
    def password_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('密码不能为空')
        return v


class RegisterRequest(BaseModel):
    """注册请求模型"""
    username: str = Field(..., min_length=3, max_length=20, description="用户名")
    password: str = Field(..., min_length=6, description="密码")
    role: str = Field(default="annotator", description="用户角色")
    
    @validator('username')
    def validate_username(cls, v):
        if not v or not v.strip():
            raise ValueError('用户名不能为空')
        
        # 检查用户名格式
        import re
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('用户名只能包含字母、数字和下划线')
        
        return v.strip()
    
    @validator('password')
    def validate_password(cls, v):
        if not v:
            raise ValueError('密码不能为空')
        if len(v) < 6:
            raise ValueError('密码长度至少6个字符')
        return v
    
    @validator('role')
    def validate_role(cls, v):
        allowed_roles = ['super_admin', 'admin', 'annotator']
        if v not in allowed_roles:
            raise ValueError(f'角色必须是以下之一: {", ".join(allowed_roles)}')
        return v


class ChangePasswordRequest(BaseModel):
    """修改密码请求模型"""
    old_password: str = Field(..., description="当前密码")
    new_password: str = Field(..., min_length=6, description="新密码")
    
    @validator('old_password')
    def old_password_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('当前密码不能为空')
        return v
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if not v:
            raise ValueError('新密码不能为空')
        if len(v) < 6:
            raise ValueError('新密码长度至少6个字符')
        return v 