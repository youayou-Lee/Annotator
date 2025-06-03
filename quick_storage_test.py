#!/usr/bin/env python3
import sys, json
from pathlib import Path

# 添加backend路径
sys.path.insert(0, str(Path.cwd() / 'backend'))

try:
    from app.core.storage import StorageManager
    storage = StorageManager()
    
    print('测试get_all_tasks...')
    tasks = storage.get_all_tasks()
    print(f'找到 {len(tasks)} 个任务')
    
    if tasks:
        task = tasks[0]
        print(f'任务ID: {task.id}')
        print(f'任务状态: {task.status}')
        
        print('测试get_task_by_id...')
        found = storage.get_task_by_id(task.id)
        print(f'get_task_by_id结果: {"找到" if found else "未找到"}')
        
        if found:
            print("✅ Storage层工作正常")
        else:
            print("❌ get_task_by_id失败")
    
except Exception as e:
    print(f'❌ 错误: {e}')
    import traceback
    traceback.print_exc() 