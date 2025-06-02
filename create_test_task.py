#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建测试任务
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def create_test_task():
    # 1. 登录获取token
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"登录失败: {response.text}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. 使用已知的admin用户ID
    admin_user_id = "user_0b072cec"  # 从用户数据中获取的admin用户ID
    print(f"Admin用户ID: {admin_user_id}")
    
    # 3. 获取可用的文档文件
    response = requests.get(f"{BASE_URL}/api/files/", headers=headers, params={"file_type": "documents"})
    if response.status_code != 200:
        print(f"获取文档文件失败: {response.text}")
        return
    
    files_data = response.json()
    document_files = files_data.get("files", [])
    
    if not document_files:
        print("没有可用的文档文件")
        return
    
    print(f"找到 {len(document_files)} 个文档文件")
    for doc in document_files:
        print(f"  - {doc['filename']}: {doc['file_path']}")
    
    # 4. 获取可用的模板文件
    response = requests.get(f"{BASE_URL}/api/files/", headers=headers, params={"file_type": "templates"})
    template_files = []
    if response.status_code == 200:
        template_data = response.json()
        template_files = template_data.get("files", [])
        print(f"找到 {len(template_files)} 个模板文件")
        for tmpl in template_files:
            print(f"  - {tmpl['filename']}: {tmpl['file_path']}")
    
    # 5. 创建任务
    task_data = {
        "name": "Admin测试任务",
        "description": "分配给admin用户的测试任务",
        "assignee_id": admin_user_id,  # 分配给admin用户
        "documents": [doc["file_path"] for doc in document_files[:2]],  # 选择前两个文档
        "template_path": template_files[0]["file_path"] if template_files else None
    }
    
    print(f"\n创建任务数据: {json.dumps(task_data, indent=2, ensure_ascii=False)}")
    
    response = requests.post(f"{BASE_URL}/api/tasks/", headers=headers, json=task_data)
    if response.status_code == 200:
        task = response.json()
        print(f"✅ 任务创建成功!")
        print(f"任务ID: {task['id']}")
        print(f"任务名称: {task['name']}")
        print(f"分配给: {task['assignee_id']}")
        print(f"文档数量: {len(task['documents'])}")
        return task["id"]
    else:
        print(f"❌ 任务创建失败: {response.text}")
        return None

if __name__ == "__main__":
    create_test_task() 