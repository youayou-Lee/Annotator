#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PostgreSQL数据库表结构检查脚本
用于验证PostgreSQL数据库中的表结构是否正确
"""

import os
import sys
import psycopg2
from psycopg2 import OperationalError
import json

def get_connection_params():
    """获取数据库连接参数"""
    return {
        "dbname": "annotator",
        "user": "postgres",
        "password": "123456",
        "host": "localhost",
        "port": "5432"
    }

def get_table_schema(cursor, table_name):
    """获取表结构"""
    # 获取表的列信息
    cursor.execute(f"""
        SELECT column_name, data_type, character_maximum_length, is_nullable
        FROM information_schema.columns
        WHERE table_name = '{table_name}'
        ORDER BY ordinal_position;
    """)
    columns = cursor.fetchall()
    
    # 获取表的主键信息
    cursor.execute(f"""
        SELECT c.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.constraint_column_usage AS ccu USING (constraint_schema, constraint_name)
        JOIN information_schema.columns AS c ON c.table_schema = tc.constraint_schema
          AND tc.table_name = c.table_name AND ccu.column_name = c.column_name
        WHERE tc.constraint_type = 'PRIMARY KEY' AND tc.table_name = '{table_name}';
    """)
    primary_keys = [pk[0] for pk in cursor.fetchall()]
    
    # 获取表的外键信息
    cursor.execute(f"""
        SELECT
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM
            information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name = '{table_name}';
    """)
    foreign_keys = cursor.fetchall()
    
    # 获取表的索引信息
    cursor.execute(f"""
        SELECT
            i.relname AS index_name,
            a.attname AS column_name,
            ix.indisunique AS is_unique
        FROM
            pg_class t,
            pg_class i,
            pg_index ix,
            pg_attribute a
        WHERE
            t.oid = ix.indrelid
            AND i.oid = ix.indexrelid
            AND a.attrelid = t.oid
            AND a.attnum = ANY(ix.indkey)
            AND t.relkind = 'r'
            AND t.relname = '{table_name}'
        ORDER BY
            i.relname;
    """)
    indexes = cursor.fetchall()
    
    # 构建表结构信息
    table_schema = {
        "name": table_name,
        "columns": [
            {
                "name": col[0],
                "type": col[1],
                "max_length": col[2],
                "nullable": col[3] == 'YES'
            } for col in columns
        ],
        "primary_keys": primary_keys,
        "foreign_keys": [
            {
                "column": fk[0],
                "references_table": fk[1],
                "references_column": fk[2]
            } for fk in foreign_keys
        ],
        "indexes": [
            {
                "name": idx[0],
                "column": idx[1],
                "unique": idx[2]
            } for idx in indexes
        ]
    }
    
    return table_schema

def check_postgres_schema():
    """检查PostgreSQL数据库表结构"""
    params = get_connection_params()
    
    print("=" * 50)
    print("PostgreSQL 表结构检查")
    print("=" * 50)
    print(f"数据库: {params['dbname']}")
    print("-" * 50)
    
    try:
        # 连接数据库
        conn = psycopg2.connect(
            dbname=params["dbname"],
            user=params["user"],
            password=params["password"],
            host=params["host"],
            port=params["port"]
        )
        
        cursor = conn.cursor()
        
        # 获取所有表
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        if not tables:
            print("数据库中没有表")
            return
        
        print(f"发现 {len(tables)} 个表:")
        for table in tables:
            table_name = table[0]
            print(f"\n表: {table_name}")
            
            # 获取表结构
            schema = get_table_schema(cursor, table_name)
            
            # 打印表列
            print("  列:")
            for column in schema["columns"]:
                col_type = f"{column['type']}"
                if column['max_length']:
                    col_type += f"({column['max_length']})"
                nullable = "NULL" if column['nullable'] else "NOT NULL"
                pk = " PRIMARY KEY" if column['name'] in schema['primary_keys'] else ""
                print(f"    - {column['name']}: {col_type} {nullable}{pk}")
            
            # 打印外键
            if schema['foreign_keys']:
                print("  外键:")
                for fk in schema['foreign_keys']:
                    print(f"    - {fk['column']} -> {fk['references_table']}({fk['references_column']})")
            
            # 打印索引
            if schema['indexes']:
                print("  索引:")
                for idx in schema['indexes']:
                    unique = "UNIQUE " if idx['unique'] else ""
                    print(f"    - {unique}INDEX {idx['name']} ({idx['column']})")
        
        # 检查用户表的记录
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"\n用户表中共有 {user_count} 条记录")
        
        if user_count > 0:
            cursor.execute("SELECT id, email, username, is_active, is_superuser FROM users")
            users = cursor.fetchall()
            print("用户列表:")
            for user in users:
                active = "活跃" if user[3] else "未激活"
                role = "管理员" if user[4] else "普通用户"
                print(f"  - ID: {user[0]}, 邮箱: {user[1]}, 用户名: {user[2]}, 状态: {active}, 角色: {role}")
        
        cursor.close()
        conn.close()
        
    except OperationalError as e:
        print("❌ 连接失败!")
        print(f"错误信息: {str(e)}")
        
    except Exception as e:
        print("❌ 发生错误!")
        print(f"错误信息: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_postgres_schema() 