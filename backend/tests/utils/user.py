import random
import string
from typing import Optional

from sqlalchemy.orm import Session

from app.services.user import create_user
from app.schemas.user import UserCreate
from app.models.user import User

from tests.utils.utils import random_email, random_lower_string

def create_random_user(db: Session) -> User:
    """创建一个随机用户，使用固定密码方便测试"""
    email = random_email()
    password = "testpass123"  # 固定密码
    username = random_lower_string()
    user_in = UserCreate(email=email, password=password, username=username)
    return create_user(db, user_in) 