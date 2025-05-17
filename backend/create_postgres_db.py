#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PostgreSQL数据库创建和初始化脚本
用于创建数据库、表结构并导入初始数据
"""

import os
import sys
import psycopg2
from psycopg2 import OperationalError
from sqlalchemy import create_engine, text

# 导入环境变量配置
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from app.core.config import settings
    from app.db.base_class import Base
    from app.models.user import User
    from app.models.task import Task
    from app.models.document import Document
    from app.models.annotation import Annotation
    from app.core.security import get_password_hash
    USING_APP_CONFIG = True
except ImportError:
    USING_APP_CONFIG = False
    from dotenv import load_dotenv
    load_dotenv()

def get_connection_params():
    """从配置或环境变量获取数据库连接参数"""
    # 硬编码正确的参数
    return {
        "dbname": "postgres",  # 连接默认数据库创建新库
        "user": "postgres",
        "password": "123456",
        "host": "localhost",
        "port": "5432"
    }

def get_db_name():
    """获取要创建的数据库名称"""
    return "annotator"

def create_database():
    """创建PostgreSQL数据库"""
    params = get_connection_params()
    db_name = get_db_name()
    
    print("=" * 50)
    print("PostgreSQL 数据库创建")
    print("=" * 50)
    print(f"连接参数: {params}")
    print(f"要创建的数据库: {db_name}")
    print("-" * 50)
    
    try:
        # 连接到默认数据库
        conn = psycopg2.connect(
            dbname=params["dbname"],
            user=params["user"],
            password=params["password"],
            host=params["host"],
            port=params["port"]
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # 检查数据库是否已存在
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        exists = cursor.fetchone()
        
        if exists:
            print(f"数据库 '{db_name}' 已存在")
        else:
            # 创建数据库
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"✅ 成功创建数据库 '{db_name}'")
        
        cursor.close()
        conn.close()
        
        return True
    
    except OperationalError as e:
        print("❌ 连接失败!")
        print(f"错误信息: {str(e)}")
        print("\n可能的原因:")
        print(" - PostgreSQL服务未启动")
        print(" - 数据库连接参数不正确")
        print(" - 权限不足")
        print("\n解决方案:")
        print(" 1. 确保PostgreSQL服务已启动")
        print(" 2. 检查连接参数是否正确")
        print(" 3. 使用具有创建数据库权限的用户")
        return False
    
    except Exception as e:
        print("❌ 发生未知错误!")
        print(f"错误信息: {str(e)}")
        import traceback
        print("\n详细错误信息:")
        traceback.print_exc()
        return False

def initialize_tables():
    """初始化数据库表结构"""
    db_name = get_db_name()
    db_user = "postgres"
    db_pass = "123456"
    db_host = "localhost"
    db_port = "5432"
    
    print("\n" + "=" * 50)
    print("数据库表初始化")
    print("=" * 50)
    
    try:
        # 创建数据库引擎
        engine_url = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
        engine = create_engine(engine_url)
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        print("✅ 成功创建所有表")
        
        return True
    
    except Exception as e:
        print("❌ 表初始化失败!")
        print(f"错误信息: {str(e)}")
        import traceback
        print("\n详细错误信息:")
        traceback.print_exc()
        return False

def create_admin_user():
    """创建管理员用户"""
    db_name = get_db_name()
    db_user = "postgres"
    db_pass = "123456"
    db_host = "localhost"
    db_port = "5432"
    
    print("\n" + "=" * 50)
    print("创建管理员用户")
    print("=" * 50)
    
    # 管理员信息
    admin_email = "admin@example.com"
    admin_username = "admin"
    admin_password = "password"
    
    try:
        # 创建数据库引擎
        engine_url = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
        engine = create_engine(engine_url)
        
        # 检查用户是否存在
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT 1 FROM users WHERE email = '{admin_email}'"))
            user_exists = result.fetchone() is not None
            
            if user_exists:
                print(f"管理员用户 '{admin_email}' 已存在")
            else:
                # 创建管理员用户
                hashed_password = get_password_hash(admin_password)
                conn.execute(text(f"""
                    INSERT INTO users (email, username, hashed_password, is_active, is_superuser)
                    VALUES ('{admin_email}', '{admin_username}', '{hashed_password}', true, true)
                """))
                conn.commit()
                print(f"✅ 成功创建管理员用户:")
                print(f" - 邮箱: {admin_email}")
                print(f" - 用户名: {admin_username}")
                print(f" - 密码: {admin_password}")
        
        return True
    
    except Exception as e:
        print("❌ 创建管理员用户失败!")
        print(f"错误信息: {str(e)}")
        import traceback
        print("\n详细错误信息:")
        traceback.print_exc()
        return False

def initialize_database():
    """初始化整个数据库"""
    if create_database():
        if initialize_tables():
            create_admin_user()
    
    print("\n完成!")
    
if __name__ == "__main__":
    initialize_database() 