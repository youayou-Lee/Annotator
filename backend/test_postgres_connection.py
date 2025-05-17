#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PostgreSQL数据库连接测试脚本
用于验证是否能成功连接到PostgreSQL数据库
"""

import os
import sys
import psycopg2
from psycopg2 import OperationalError

# 导入环境变量配置
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from app.core.config import settings
    USING_APP_CONFIG = True
except ImportError:
    USING_APP_CONFIG = False
    from dotenv import load_dotenv
    load_dotenv()

def get_connection_params():
    """从配置或环境变量获取数据库连接参数"""
    # 直接读取.env文件
    with open('.env', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

    # 硬编码正确的参数
    return {
        "dbname": "annotator",
        "user": "postgres",
        "password": "123456",
        "host": "localhost",
        "port": "5432"
    }

def get_connection_string():
    """获取数据库连接字符串"""
    if USING_APP_CONFIG:
        return settings.DATABASE_URL
    else:
        return os.getenv("DATABASE_URL", "postgresql://postgres:123456@localhost:5432/annotator")

def test_connection():
    """测试数据库连接"""
    params = get_connection_params()
    
    print("=" * 50)
    print("PostgreSQL 连接测试")
    print("=" * 50)
    print(f"连接参数: {params}")
    print(f"连接字符串: postgresql://{params['user']}:{params['password']}@{params['host']}:{params['port']}/{params['dbname']}")
    print("-" * 50)
    
    try:
        # 尝试连接
        conn = psycopg2.connect(
            dbname=params["dbname"],
            user=params["user"],
            password=params["password"],
            host=params["host"],
            port=params["port"]
        )
        
        # 获取数据库版本
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        # 获取数据库表信息
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        print("✅ 连接成功!")
        print(f"数据库版本: {version[0]}")
        print("\n数据库表:")
        if tables:
            for table in tables:
                print(f" - {table[0]}")
        else:
            print(" - 没有找到表")
        
        # 检查是否有users表并有记录
        if any(table[0] == 'users' for table in tables):
            cursor.execute("SELECT COUNT(*) FROM users;")
            user_count = cursor.fetchone()[0]
            print(f"\nusers表中的用户数量: {user_count}")
            
            if user_count > 0:
                cursor.execute("SELECT id, email, username FROM users LIMIT 5;")
                users = cursor.fetchall()
                print("\n用户列表 (前5个):")
                for user in users:
                    print(f" - ID: {user[0]}, 邮箱: {user[1]}, 用户名: {user[2]}")
        
        # 关闭连接
        cursor.close()
        conn.close()
        
    except OperationalError as e:
        print("❌ 连接失败!")
        print(f"错误信息: {str(e)}")
        print("\n可能的原因:")
        print(" - PostgreSQL服务未启动")
        print(" - 数据库连接参数不正确")
        print(" - 数据库不存在")
        print(" - 网络问题")
        print("\n解决方案:")
        print(" 1. 确保PostgreSQL服务已启动")
        print(" 2. 检查连接参数是否正确")
        print(" 3. 创建数据库: CREATE DATABASE annotator;")
        print(" 4. 确保防火墙允许连接")
        
    except Exception as e:
        print("❌ 发生未知错误!")
        print(f"错误信息: {str(e)}")
        print(f"错误类型: {type(e).__name__}")
        import traceback
        print("\n详细错误信息:")
        traceback.print_exc()

if __name__ == "__main__":
    test_connection() 