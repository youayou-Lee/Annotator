#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试API文档校验功能
"""

import requests
import json
import time

def test_api_validation():
    """测试API文档校验功能"""
    print("=== API文档校验功能测试 ===\n")
    
    # API基础URL
    base_url = "http://localhost:8000"
    
    # 等待服务器启动
    print("1. 等待服务器启动...")
    for i in range(10):
        try:
            response = requests.get(f"{base_url}/", timeout=5)
            if response.status_code == 200:
                print("✅ 服务器已启动")
                break
        except:
            print(f"   等待中... ({i+1}/10)")
            time.sleep(2)
    else:
        print("❌ 服务器启动超时")
        return False
    
    # 登录获取token
    print("\n2. 登录获取token...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ 登录成功")
        else:
            print(f"❌ 登录失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 登录请求失败: {e}")
        return False
    
    # 测试创建任务（使用有效文档）
    print("\n3. 测试创建任务（有效文档）...")
    valid_task_data = {
        "name": "测试任务-有效文档",
        "description": "测试文档校验功能",
        "documents": ["public_files\\documents\\20250605_123812_test_template.json"],
        "template_path": "public_files\\templates\\20250605_122824_test_template.py"
    }
    
    try:
        response = requests.post(f"{base_url}/api/tasks/", json=valid_task_data, headers=headers)
        if response.status_code == 200:
            print("✅ 有效文档任务创建成功")
            task_id = response.json()["id"]
            print(f"   任务ID: {task_id}")
        else:
            print(f"❌ 有效文档任务创建失败: {response.text}")
    except Exception as e:
        print(f"❌ 有效文档任务创建请求失败: {e}")
    
    # 测试创建任务（使用无效文档）
    print("\n4. 测试创建任务（无效文档）...")
    invalid_task_data = {
        "name": "测试任务-无效文档",
        "description": "测试文档校验功能",
        "documents": ["public_files\\documents\\test_invalid_data.json"],
        "template_path": "public_files\\templates\\20250605_122824_test_template.py"
    }
    
    try:
        response = requests.post(f"{base_url}/api/tasks/", json=invalid_task_data, headers=headers)
        if response.status_code == 400:
            error_detail = response.json()["detail"]
            print("✅ 无效文档任务创建被正确拒绝")
            print("   错误信息:")
            print(f"   {error_detail}")
        else:
            print(f"❌ 无效文档任务应该被拒绝但创建成功了: {response.text}")
    except Exception as e:
        print(f"❌ 无效文档任务创建请求失败: {e}")
    
    print("\n🎉 API文档校验功能测试完成！")
    return True

if __name__ == "__main__":
    test_api_validation()
 