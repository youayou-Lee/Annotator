#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查任务数据
"""

import json
from pathlib import Path
import requests

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

def check_task_consistency():
    """检查API返回的任务和文件系统中的任务是否一致"""
    
    print("🔍 检查任务数据一致性...")
    
    # 登录并获取任务
    login_response = requests.post('http://localhost:8000/api/auth/login', json={'username': 'admin', 'password': 'admin123'})
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # 获取任务列表
    tasks_response = requests.get('http://localhost:8000/api/tasks', headers=headers)
    api_tasks = tasks_response.json()['tasks']

    print('📡 API返回的任务:')
    for task in api_tasks:
        print(f'  ID: {task["id"]}')
        print(f'  名称: {task["name"]}')
        print(f'  分配给: {task.get("assignee_id")}')

    # 检查文件系统中的任务
    tasks_file = Path('data/tasks/tasks.json')
    if tasks_file.exists():
        with open(tasks_file, 'r', encoding='utf-8') as f:
            file_tasks_data = json.load(f)
            file_tasks = file_tasks_data['tasks']
        
        print('\n📁 文件系统中的任务:')
        for task in file_tasks:
            print(f'  ID: {task["id"]}')
            print(f'  名称: {task["name"]}')
            print(f'  分配给: {task.get("assignee_id")}')
    
    # 检查目录结构
    print('\n📂 任务目录结构:')
    tasks_dir = Path('data/tasks')
    if tasks_dir.exists():
        for item in tasks_dir.iterdir():
            if item.is_dir():
                print(f'  📁 {item.name}/')
                
                # 检查annotations目录
                annotations_dir = item / 'annotations'
                if annotations_dir.exists():
                    ann_files = list(annotations_dir.glob('*.json'))
                    print(f'    📄 标注文件: {len(ann_files)}')
                    for ann_file in ann_files:
                        size = ann_file.stat().st_size
                        print(f'      {ann_file.name}: {size} 字节')

    # 分析不一致的原因
    if api_tasks and file_tasks:
        api_task_ids = [t['id'] for t in api_tasks]
        file_task_ids = [t['id'] for t in file_tasks]
        
        if api_task_ids != file_task_ids:
            print('\n⚠️  API和文件系统任务ID不一致!')
            print(f'   API任务ID: {api_task_ids}')
            print(f'   文件任务ID: {file_task_ids}')
        else:
            print('\n✅ API和文件系统任务ID一致')

if __name__ == "__main__":
    check_task_data()
    check_task_consistency() 