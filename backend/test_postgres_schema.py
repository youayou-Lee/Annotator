#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PostgreSQL数据库结构测试脚本
用于验证数据库表结构是否正确
"""

import os
import sys
from sqlalchemy import create_engine, text, MetaData, inspect

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.db.session import engine

def test_tables():
    """测试数据库表结构"""
    print("=" * 50)
    print("PostgreSQL 数据库表结构测试")
    print("=" * 50)
    
    try:
        # 获取表信息
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        
        if not table_names:
            print("❌ 数据库中没有表！请先运行初始化脚本。")
            return False
        
        print(f"发现 {len(table_names)} 个表:")
        for table_name in sorted(table_names):
            print(f" - {table_name}")
            
            # 获取表的列信息
            columns = inspector.get_columns(table_name)
            print(f"   列数: {len(columns)}")
            
            # 获取主键
            primary_keys = inspector.get_pk_constraint(table_name)
            print(f"   主键: {primary_keys['constrained_columns']}")
            
            # 获取外键
            foreign_keys = inspector.get_foreign_keys(table_name)
            if foreign_keys:
                print(f"   外键数: {len(foreign_keys)}")
                for fk in foreign_keys:
                    print(f"     - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
            
            # 获取索引
            indexes = inspector.get_indexes(table_name)
            if indexes:
                print(f"   索引数: {len(indexes)}")
                for idx in indexes:
                    print(f"     - {idx['name']}: {idx['column_names']}")
            
            print("")
        
        # 检查必要的表是否存在
        required_tables = ["users", "documents", "tasks", "annotations", "annotation_history", 
                          "annotation_reviews", "export_tasks"]
        missing_tables = [table for table in required_tables if table not in table_names]
        
        if missing_tables:
            print(f"❌ 缺少必要的表: {missing_tables}")
            return False
        
        print("✅ 所有必要的表都存在")
        
        # 检查用户表是否有记录
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            user_count = result.scalar()
            print(f"用户表中有 {user_count} 条记录")
            
            if user_count > 0:
                print("用户列表:")
                result = conn.execute(text("SELECT id, email, username, is_superuser FROM users"))
                for row in result:
                    print(f" - ID: {row[0]}, 邮箱: {row[1]}, 用户名: {row[2]}, 超级用户: {row[3]}")
        
        return True
    
    except Exception as e:
        print(f"❌ 测试数据库表结构时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_tables()
    sys.exit(0 if success else 1) 