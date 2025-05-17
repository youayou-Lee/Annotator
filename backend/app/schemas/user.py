from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from enum import Enum

class UserRole(str, Enum):
    superuser = "superuser"
    admin = "admin"
    annotator = "annotator"

class UserStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class UserBase(BaseModel):
    email: EmailStr
    username: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    role: Optional[UserRole] = UserRole.annotator

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserApproval(BaseModel):
    status: UserStatus
    reason: Optional[str] = None

class UserInDBBase(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    status: UserStatus = UserStatus.pending
    approval_date: Optional[datetime] = None
    approved_by_id: Optional[int] = None

    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str

class UserWithApprovedUsers(User):
    approved_users: List["User"] = []

class ApprovalRequest(BaseModel):
    user_id: int
    status: UserStatus
    reason: Optional[str] = None 