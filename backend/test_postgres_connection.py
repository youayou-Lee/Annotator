#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PostgreSQL数据库连接测试脚本
用于验证是否能成功连接到PostgreSQL数据库
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 添加项目根目录到Python路径
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

# 手动加载.env文件
ENV_FILE = os.path.join(ROOT_DIR, '.env')
print(f"尝试加载.env文件: {ENV_FILE}")
if os.path.exists(ENV_FILE):
    print(f".env文件存在: {ENV_FILE}")
    load_dotenv(ENV_FILE)
else:
    print(f"警告: .env文件不存在: {ENV_FILE}")

from app.core.config import settings

def test_postgres_connection():
    """测试PostgreSQL连接"""
    print("=" * 50)
    print("PostgreSQL 连接测试")
    print("=" * 50)
    
    # 打印环境变量和配置信息
    print(f"当前目录: {os.getcwd()}")
    print(f"当前环境变量DATABASE_URL: {os.getenv('DATABASE_URL', '未设置')}")
    
    # 打印配置中的连接信息
    print(f"配置中的DATABASE_URL: {settings.DATABASE_URL}")
    print(f"实际使用的连接字符串: {settings.SQLALCHEMY_DATABASE_URI}")
    print(f"用户名: {settings.POSTGRES_USER}")
    print(f"密码: {'*' * len(settings.POSTGRES_PASSWORD) if settings.POSTGRES_PASSWORD else '未设置'} (长度: {len(settings.POSTGRES_PASSWORD) if settings.POSTGRES_PASSWORD else 0})")
    print(f"数据库: {settings.POSTGRES_DB}")
    print(f"主机: {settings.POSTGRES_HOST}")
    print(f"端口: {settings.POSTGRES_PORT}")
    
    # 尝试从.env文件创建连接
    env_db_url = os.getenv('DATABASE_URL')
    if env_db_url:
        print(f"\n尝试使用.env中的DATABASE_URL直接连接:")
        print(f"连接字符串: {env_db_url}")
        try:
            engine = create_engine(env_db_url)
            with engine.connect():
                print("✅ 使用.env中的连接字符串连接成功!")
        except Exception as e:
            print(f"❌ 使用.env中的连接字符串连接失败: {str(e)}")
    
    print("-" * 50)
    
    try:
        # 创建数据库引擎
        engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
        
        # 测试连接
        with engine.connect() as connection:
            # 获取数据库版本
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ 连接成功! PostgreSQL版本: {version}")
            
            # 测试数据库用户
            result = connection.execute(text("SELECT current_user;"))
            user = result.fetchone()[0]
            print(f"当前数据库用户: {user}")
            
            # 检查当前数据库
            result = connection.execute(text("SELECT current_database();"))
            db = result.fetchone()[0]
            print(f"当前数据库: {db}")
            
            # 检查数据库表
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = result.fetchall()
            
            print("\n数据库表:")
            if tables:
                for table in tables:
                    print(f" - {table[0]}")
            else:
                print(" - 没有找到表")
            
            return True
    except Exception as e:
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
        return False

if __name__ == "__main__":
    success = test_postgres_connection()
    sys.exit(0 if success else 1) 