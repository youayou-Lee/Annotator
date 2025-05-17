#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PostgreSQL数据库初始化脚本
用于创建数据库和初始化表结构
"""

import os
import sys
from sqlalchemy import create_engine, text
import bcrypt
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.db.base_class import Base
from app.db.session import engine
from app.models.user import User
# 确保所有模型都被导入，这样Base.metadata才包含所有表
from app.db.base import Base  # 这会导入所有模型

def create_database():
    """创建数据库"""
    # 获取PostgreSQL连接信息
    pg_url = settings.SQLALCHEMY_DATABASE_URI
    db_name = settings.POSTGRES_DB
    
    # 创建一个连接到postgres数据库的引擎，用于创建新数据库
    base_url = pg_url.rsplit('/', 1)[0] + '/postgres'
    base_engine = create_engine(base_url)
    
    print(f"正在检查数据库 '{db_name}' 是否存在...")
    
    try:
        with base_engine.connect() as conn:
            # 检查数据库是否存在
            result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"))
            exists = result.scalar() is not None
            
            if exists:
                print(f"数据库 '{db_name}' 已存在.")
            else:
                print(f"数据库 '{db_name}' 不存在，正在创建...")
                # 创建新的连接，因为我们不能在事务中创建数据库
                conn.execution_options(isolation_level="AUTOCOMMIT").execute(text(f"CREATE DATABASE {db_name}"))
                print(f"数据库 '{db_name}' 创建成功！")
    
    except Exception as e:
        print(f"创建数据库时出错: {str(e)}")
        return False
    
    return True

def init_database():
    """初始化数据库表结构"""
    print("正在初始化数据库表结构...")
    
    try:
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        print("数据库表创建成功！")
        return True
    except Exception as e:
        print(f"创建数据库表时出错: {str(e)}")
        return False

def create_admin_user():
    """创建管理员用户"""
    from sqlalchemy.orm import sessionmaker
    
    # 创建会话
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 检查是否已存在管理员用户
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        
        if admin:
            print("管理员用户已存在.")
        else:
            print("正在创建管理员用户...")
            # 生成密码哈希
            hashed_password = bcrypt.hashpw("admin".encode(), bcrypt.gensalt()).decode()
            
            # 创建管理员用户
            admin = User(
                email="admin@example.com",
                username="admin",
                hashed_password=hashed_password,
                is_active=True,
                is_superuser=True
            )
            
            db.add(admin)
            db.commit()
            print("管理员用户创建成功！")
            print("用户名: admin@example.com")
            print("密码: admin")
        
        return True
    except Exception as e:
        db.rollback()
        print(f"创建管理员用户时出错: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 50)
    print("PostgreSQL 数据库初始化")
    print("=" * 50)
    
    if create_database():
        if init_database():
            if create_admin_user():
                print("\n✅ 数据库初始化完成！")
                sys.exit(0)
    
    print("\n❌ 数据库初始化失败！")
    sys.exit(1) 