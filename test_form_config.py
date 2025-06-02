#!/usr/bin/env python3
"""
调试表单配置API返回的数据结构
"""

import requests
import json

def debug_form_config():
    base_url = "http://localhost:8000"
    
    # 1. 登录获取token
    login_response = requests.post(
        f"{base_url}/api/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    
    if login_response.status_code != 200:
        print(f"登录失败: {login_response.status_code}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. 获取表单配置
    print("=== 表单配置API ===")
    config_response = requests.get(
        f"{base_url}/api/annotations/task_1339355d/documents/doc_be0758a9/form-config", 
        headers=headers
    )
    print(f"状态码: {config_response.status_code}")
    if config_response.status_code == 200:
        config_data = config_response.json()
        print(f"完整响应: {json.dumps(config_data, indent=2, ensure_ascii=False)}")
        
        fields = config_data.get("fields", [])
        print(f"\n字段数量: {len(fields)}")
        
        if fields:
            print("\n前3个字段详情:")
            for i, field in enumerate(fields[:3]):
                print(f"字段 {i+1}: {json.dumps(field, indent=2, ensure_ascii=False)}")
    else:
        print(f"错误: {config_response.text}")

if __name__ == "__main__":
    debug_form_config() 