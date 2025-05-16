#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
创建管理员用户的脚本
"""

import sys
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.services.user import get_user_by_email

def create_admin_user(db: Session, email: str, username: str, password: str) -> User:
    """创建管理员用户"""
    # 检查用户是否已存在
    user = get_user_by_email(db, email)
    if user:
        print(f"用户 {email} 已存在")
        return user
    
    # 创建新用户
    user = User(
        email=email,
        username=username,
        hashed_password=get_password_hash(password),
        is_active=True,
        is_superuser=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"管理员用户 {email} 创建成功")
    return user

def main():
    """主函数"""
    # 默认管理员信息
    email = "admin@example.com"
    username = "admin"
    password = "admin123"
    
    # 命令行参数解析
    if len(sys.argv) > 1:
        email = sys.argv[1]
    if len(sys.argv) > 2:
        username = sys.argv[2]
    if len(sys.argv) > 3:
        password = sys.argv[3]
    
    # 创建数据库会话
    db = SessionLocal()
    try:
        create_admin_user(db, email, username, password)
    finally:
        db.close()

if __name__ == "__main__":
    main() 