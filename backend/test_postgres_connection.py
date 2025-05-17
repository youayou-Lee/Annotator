#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PostgreSQL数据库连接测试脚本
用于验证是否能成功连接到PostgreSQL数据库
"""

import os
import sys
from sqlalchemy import create_engine, text

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings

def test_postgres_connection():
    """测试PostgreSQL连接"""
    print("=" * 50)
    print("PostgreSQL 连接测试")
    print("=" * 50)
    print(f"连接字符串: {settings.SQLALCHEMY_DATABASE_URI}")
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