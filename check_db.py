import psycopg2
import sys

# 从.env文件中获取的数据库连接参数
db_params = {
    "user": "postgres",
    "password": "123456",
    "host": "localhost",
    "port": "5432",
    "database": "annotator"
}

try:
    print("正在连接到 PostgreSQL 数据库...")
    conn = psycopg2.connect(**db_params)
    
    cur = conn.cursor()
    print("PostgreSQL 数据库连接成功")
    
    # 获取 PostgreSQL 数据库版本
    cur.execute("SELECT version();")
    db_version = cur.fetchone()
    print(f"PostgreSQL 数据库版本: {db_version}")
    
    # 检查users表中的数据
    try:
        print("\n=== 用户表数据 ===")
        cur.execute("SELECT COUNT(*) FROM users")
        count = cur.fetchone()[0]
        print(f"用户表中共有 {count} 条记录")
        
        print("\n=== 所有用户ID ===")
        cur.execute("SELECT id FROM users ORDER BY id")
        ids = cur.fetchall()
        for id_row in ids:
            print(f"  - ID: {id_row[0]}")
        
        print("\n=== 详细用户数据 ===")
        cur.execute("SELECT id, email, username, is_active, role, status FROM users ORDER BY id")
        users = cur.fetchall()
        for user in users:
            print(f"  - ID: {user[0]}, 邮箱: {user[1]}, 用户名: {user[2]}, 角色: {user[4]}, 状态: {user[5]}")
        
        print("\n=== 注册但未获批准的用户 ===")
        cur.execute("SELECT id, email, username, role, status FROM users WHERE status != 'approved'")
        pending_users = cur.fetchall()
        if pending_users:
            for user in pending_users:
                print(f"  - ID: {user[0]}, 邮箱: {user[1]}, 用户名: {user[2]}, 角色: {user[3]}, 状态: {user[4]}")
                
                # 自动询问是否要更新该用户状态
                print(f"是否将用户 {user[2]} (ID: {user[0]}) 的状态更新为 'approved'?")
                confirm = input("确认更新? (y/n): ")
                if confirm.lower() == 'y':
                    cur.execute("UPDATE users SET status = 'approved' WHERE id = %s", (user[0],))
                    conn.commit()
                    print(f"用户 {user[2]} (ID: {user[0]}) 状态已更新为 'approved'")
        else:
            print("  没有等待批准的用户")
            
    except Exception as e:
        print(f"查询users表时出错: {e}")
        # 尝试获取表结构
        cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'users'")
        columns = cur.fetchall()
        print("users表结构:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]}")
    
    cur.close()
except (Exception, psycopg2.DatabaseError) as error:
    print(f"错误: {error}")
    sys.exit(1)
finally:
    if conn is not None:
        conn.close()
        print("\n数据库连接已关闭") 