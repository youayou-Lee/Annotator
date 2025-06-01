from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from enum import Enum


class UserRole(str, Enum):
    """用户角色枚举"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    ANNOTATOR = "annotator"


class UserBase(BaseModel):
    """用户基础模型"""
    username: str
    role: UserRole = UserRole.ANNOTATOR


class UserCreate(UserBase):
    """创建用户模型"""
    password: str


class UserUpdate(BaseModel):
    """更新用户模型"""
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None


class User(UserBase):
    """用户响应模型"""
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserInDB(User):
    """数据库中的用户模型"""
    password_hash: str 