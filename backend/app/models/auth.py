from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    """JWT令牌模型"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """令牌数据模型"""
    username: Optional[str] = None
    user_id: Optional[str] = None


class LoginRequest(BaseModel):
    """登录请求模型"""
    username: str
    password: str


class RegisterRequest(BaseModel):
    """注册请求模型"""
    username: str
    password: str
    role: str = "annotator" 