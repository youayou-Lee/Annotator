#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json

def test_task_creation():
    """测试任务创建API"""
    
    # API基础URL
    base_url = "http://localhost:8000/api"
    
    # 首先登录获取token
    login_data = {
        "username": "admin",  # 假设有这个用户
        "password": "admin123"
    }
    
    try:
        # 登录
        login_response = requests.post(f"{base_url}/auth/login", json=login_data)
        if login_response.status_code != 200:
            print(f"登录失败: {login_response.status_code}")
            print(login_response.text)
            return
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # 获取文件列表
        files_response = requests.get(f"{base_url}/files", headers=headers)
        if files_response.status_code != 200:
            print(f"获取文件列表失败: {files_response.status_code}")
            return
        
        files_data = files_response.json()
        print("文件列表:", json.dumps(files_data, indent=2, ensure_ascii=False))
        
        # 查找文档和模板文件
        documents = [f for f in files_data.get("files", []) if f.get("file_type") == "documents"]
        templates = [f for f in files_data.get("files", []) if f.get("file_type") == "templates"]
        
        if not documents:
            print("没有找到文档文件")
            return
        
        if not templates:
            print("没有找到模板文件")
            return
        
        # 创建任务
        task_data = {
            "name": "测试任务",
            "description": "这是一个测试任务",
            "documents": [documents[0]["file_path"]],  # 使用第一个文档的路径
            "template_path": "public_files/templates/fixed_news_template.py"  # 使用修复后的模板
        }
        
        print("创建任务数据:", json.dumps(task_data, indent=2, ensure_ascii=False))
        
        task_response = requests.post(f"{base_url}/tasks/", json=task_data, headers=headers)
        print(f"任务创建响应状态: {task_response.status_code}")
        print("响应内容:", task_response.text)
        
        if task_response.status_code == 200:
            print("任务创建成功!")
        else:
            print("任务创建失败!")
            
    except Exception as e:
        print(f"测试过程中出现错误: {e}")

if __name__ == "__main__":
    test_task_creation() 