#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
创建管理员用户的简化脚本，不使用ORM关系
"""

import sqlite3
import os
from app.core.security import get_password_hash

def create_admin_user():
    """创建管理员用户"""
    # 数据库路径
    db_path = "annotator.db"  # 默认SQLite数据库路径
    
    # 检查数据库是否存在
    if not os.path.exists(db_path):
        print(f"错误: 数据库文件 {db_path} 不存在")
        return False
    
    # 默认管理员信息
    email = "admin@example.com"
    username = "admin"
    password = "password"  # 简单密码方便测试
    hashed_password = get_password_hash(password)
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 查询是否已有此用户
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        if user:
            print(f"用户 {email} 已存在")
            return True
        
        # 插入新用户
        cursor.execute(
            """
            INSERT INTO users (email, username, hashed_password, is_active, is_superuser)
            VALUES (?, ?, ?, ?, ?)
            """,
            (email, username, hashed_password, 1, 1)
        )
        
        conn.commit()
        print(f"管理员用户 {email} 创建成功!")
        print(f"用户名: {username}")
        print(f"密码: {password}")
        return True
        
    except Exception as e:
        print(f"创建用户时发生错误: {e}")
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    create_admin_user() 