#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
创建管理员用户的简化脚本，避开ORM依赖
直接使用SQL创建用户或更新现有用户
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2
import bcrypt
from sqlalchemy import create_engine, text

# 加载环境变量
load_dotenv()

# 获取数据库连接字符串
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("错误: 未找到DATABASE_URL环境变量")
    exit(1)

def create_or_update_admin_user(email="admin@example.com", username="admin", password="password"):
    """直接使用SQL创建管理员用户或更新现有用户"""
    try:
        # 创建SQLAlchemy引擎
        engine = create_engine(DATABASE_URL)
        
        # 生成密码哈希
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        
        # 使用SQL创建或更新用户
        with engine.connect() as conn:
            # 检查用户是否已存在
            result = conn.execute(text("SELECT * FROM users WHERE email = :email"), {"email": email})
            user = result.fetchone()
            
            if user:
                print(f"用户 {email} 已存在，正在更新...")
                # 更新用户
                conn.execute(
                    text("""
                    UPDATE users 
                    SET hashed_password = :hashed_password, 
                        is_active = true, 
                        is_superuser = true,
                        role = 'superuser',
                        status = 'approved'
                    WHERE email = :email
                    """),
                    {
                        "email": email,
                        "hashed_password": hashed_password
                    }
                )
                conn.commit()
                print(f"管理员用户 {email} 更新成功")
            else:
                # 创建用户
                conn.execute(
                    text("""
                    INSERT INTO users 
                    (email, username, hashed_password, is_active, is_superuser, role, status) 
                    VALUES (:email, :username, :hashed_password, true, true, 'superuser', 'approved')
                    """),
                    {
                        "email": email,
                        "username": username,
                        "hashed_password": hashed_password
                    }
                )
                conn.commit()
                print(f"管理员用户 {email} 创建成功")
            
            print(f"用户名: {email}")
            print(f"密码: {password}")
            return True
            
    except Exception as e:
        print(f"创建或更新用户时出错: {str(e)}")
        return False

if __name__ == "__main__":
    # 如果命令行参数提供了用户名和密码，则使用提供的值
    email = "admin@example.com"
    username = "admin"
    password = "password"
    
    if len(sys.argv) > 1:
        email = sys.argv[1]
    if len(sys.argv) > 2:
        username = sys.argv[2]
    if len(sys.argv) > 3:
        password = sys.argv[3]
        
    create_or_update_admin_user(email, username, password) 