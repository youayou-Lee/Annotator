#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试标注数据验证功能
"""

import requests
import json

# 配置
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/auth/login"
SAVE_ANNOTATION_URL = f"{BASE_URL}/api/annotations/{{task_id}}/documents/{{document_id}}/annotation"

def login():
    """登录获取token"""
    login_data = {
        "username": "admin", 
        "password": "admin123"
    }
    
    response = requests.post(LOGIN_URL, json=login_data)
    if response.status_code == 200:
        result = response.json()
        return result.get("access_token")
    else:
        print(f"登录失败: {response.status_code} - {response.text}")
        return None

def test_pydantic_validation():
    """测试Pydantic校验功能"""
    print("=== 测试Pydantic校验功能 ===")
    
    # 登录获取token
    token = login()
    if not token:
        print("无法获取访问令牌")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 使用已知的任务和文档ID（这里需要根据实际情况调整）
    task_id = "task_ca3b81ad"
    document_id = "doc_f3830c3a"
    
    # 测试1: 有效数据
    print("\n1. 测试有效数据...")
    valid_data = {
        "annotation_data": {
            "案件描述": "这是一个测试案件描述",
            "构成原因": "构成某种犯罪的原因",
            "嫌疑人": "张三",
            "罪名": "盗窃罪",
            "基准刑_年": "2",
            "基准刑_月": "6",
            "相似罪名": [
                {
                    "罪名": "抢劫罪",
                    "不构成原因": "没有使用暴力"
                }
            ]
        }
    }
    
    url = SAVE_ANNOTATION_URL.format(task_id=task_id, document_id=document_id)
    response = requests.post(url, headers=headers, json=valid_data)
    
    if response.status_code == 200:
        print("✅ 有效数据保存成功")
    else:
        print(f"❌ 有效数据保存失败: {response.status_code}")
        print(f"响应: {response.text}")
    
    # 测试2: 无效数据 - 月份超过12
    print("\n2. 测试无效数据（月份超过12）...")
    invalid_data_months = {
        "annotation_data": {
            "案件描述": "测试案件",
            "构成原因": "构成原因",
            "嫌疑人": "李四",
            "罪名": "盗窃罪",
            "基准刑_年": "2",
            "基准刑_月": "15",  # 违反约束：月份应该小于12
            "相似罪名": []
        }
    }
    
    response = requests.post(url, headers=headers, json=invalid_data_months)
    
    if response.status_code == 400:
        print("✅ 正确检测到月份超过12的错误")
        print(f"错误详情: {response.text}")
    else:
        print(f"❌ 未能检测到月份错误: {response.status_code}")
        print(f"响应: {response.text}")
    
    # 测试3: 无效数据 - 刑期过长
    print("\n3. 测试无效数据（刑期过长）...")
    invalid_data_sentence = {
        "annotation_data": {
            "案件描述": "测试案件",
            "构成原因": "构成原因",
            "嫌疑人": "王五",
            "罪名": "盗窃罪",
            "基准刑_年": "15",  # 违反约束：总刑期超过10年
            "基准刑_月": "0",
            "相似罪名": []
        }
    }
    
    response = requests.post(url, headers=headers, json=invalid_data_sentence)
    
    if response.status_code == 400:
        print("✅ 正确检测到刑期过长的错误")
        print(f"错误详情: {response.text}")
    else:
        print(f"❌ 未能检测到刑期错误: {response.status_code}")
        print(f"响应: {response.text}")
    
    # 测试4: 无效数据 - 必填字段为空
    print("\n4. 测试无效数据（必填字段为空）...")
    invalid_data_required = {
        "annotation_data": {
            "案件描述": "",  # 可能为空
            "构成原因": "",  # 根据模板可能是必填的
            "嫌疑人": "",    # 必填字段为空
            "罪名": "",      # 必填字段为空
            "基准刑_年": "0",
            "基准刑_月": "0",
            "相似罪名": []
        }
    }
    
    response = requests.post(url, headers=headers, json=invalid_data_required)
    
    if response.status_code == 400:
        print("✅ 正确检测到必填字段为空的错误")
        print(f"错误详情: {response.text}")
    else:
        print(f"❌ 未能检测到必填字段错误: {response.status_code}")
        print(f"响应: {response.text}")

if __name__ == "__main__":
    test_pydantic_validation() 