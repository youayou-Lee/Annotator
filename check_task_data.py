#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查任务数据
"""

import json
from pathlib import Path

def check_task_data():
    tasks_file = Path('backend/data/tasks/tasks.json')
    if not tasks_file.exists():
        print("任务文件不存在")
        return
    
    with open(tasks_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("=== 任务数据检查 ===")
    for task in data.get('tasks', []):
        print(f"\n任务ID: {task['id']}")
        print(f"任务名称: {task.get('name', 'N/A')}")
        print(f"分配给: {task.get('assignee_id', '未分配')}")
        print(f"创建者: {task.get('creator_id', 'N/A')}")
        print(f"状态: {task.get('status', 'N/A')}")
        print(f"模板: {task.get('template', {}).get('file_path', '无模板') if task.get('template') else '无模板'}")
        
        documents = task.get('documents', [])
        print(f"文档数量: {len(documents)}")
        
        for i, doc in enumerate(documents):
            print(f"  文档{i+1}:")
            print(f"    ID: {doc['id']}")
            print(f"    文件名: {doc.get('filename', 'N/A')}")
            print(f"    路径: {doc.get('file_path', 'N/A')}")
            print(f"    状态: {doc.get('status', 'N/A')}")
            
            # 检查文件是否存在
            file_path = Path('backend/data') / doc.get('file_path', '')
            exists = file_path.exists()
            print(f"    文件存在: {exists}")
            if not exists:
                print(f"    完整路径: {file_path.absolute()}")
        
        print("-" * 50)

if __name__ == "__main__":
    check_task_data() 