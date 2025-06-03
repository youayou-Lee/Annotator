#!/usr/bin/env python3
"""
测试form-config API端点的脚本
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_form_config_api():
    """测试form-config API"""
    
    # 1. 首先登录获取token
    print("1. 登录获取token...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ 登录失败: {response.text}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✅ 登录成功，token: {token[:20]}...")
    
    # 2. 测试有问题的API端点
    task_id = "task_f946d1d6"
    document_id = "doc_35774d2b"
    
    print(f"\n2. 测试form-config API - task: {task_id}, doc: {document_id}")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/annotations/{task_id}/documents/{document_id}/form-config",
            headers=headers
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            print("✅ form-config API 调用成功！")
            data = response.json()
            print(f"   字段数量: {len(data.get('fields', []))}")
            print(f"   模板信息: {data.get('template_info', {})}")
        elif response.status_code == 404:
            print("⚠️  任务或文档不存在")
        elif response.status_code == 500:
            print("❌ 服务器内部错误 - 可能是我们要修复的问题")
        else:
            print(f"❌ 其他错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

if __name__ == "__main__":
    test_form_config_api() 