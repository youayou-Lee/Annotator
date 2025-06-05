#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试当前的400错误问题
"""

import requests
import json

# 配置
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/auth/login"
SAVE_ANNOTATION_URL = f"{BASE_URL}/api/annotations/task_88044250/documents/doc_2fe74170/annotation"

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

def test_400_error():
    """测试重现400错误"""
    print("=== 测试400错误问题 ===")
    
    # 登录获取token
    token = login()
    if not token:
        print("无法获取访问令牌")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 测试数据1 - 测试61这个值（超过12的月份）
    print("\n1. 测试61月份（应该报错）...")
    test_data1 = {
        "annotation_data": {
            "案件描述": "这是一个测试案件",
            "构成原因": "构成某种犯罪的原因",
            "嫌疑人": "张三",
            "罪名": "盗窃罪",
            "基准刑_年": 3,
            "基准刑_月": 61,  # 这应该触发"月份应该小于12"的错误
            "相似罪名": []
        }
    }
    
    response = requests.post(SAVE_ANNOTATION_URL, headers=headers, json=test_data1)
    print(f"响应状态码: {response.status_code}")
    if response.status_code != 200:
        print(f"响应内容: {response.text}")
        try:
            error_detail = response.json()
            print(f"错误详情JSON: {json.dumps(error_detail, ensure_ascii=False, indent=2)}")
        except:
            print("❌ 无法解析错误详情JSON")
    else:
        print("✅ 保存成功")
    
    # 测试数据2 - 测试超过10年的刑期
    print("\n2. 测试超过10年的刑期...")
    test_data2 = {
        "annotation_data": {
            "案件描述": "这是一个测试案件",
            "构成原因": "构成某种犯罪的原因",
            "嫌疑人": "张三",
            "罪名": "盗窃罪",
            "基准刑_年": 15,  # 15年超过10年限制
            "基准刑_月": 0,
            "相似罪名": []
        }
    }
    
    response = requests.post(SAVE_ANNOTATION_URL, headers=headers, json=test_data2)
    print(f"响应状态码: {response.status_code}")
    if response.status_code != 200:
        print(f"响应内容: {response.text}")
        try:
            error_detail = response.json()
            print(f"错误详情JSON: {json.dumps(error_detail, ensure_ascii=False, indent=2)}")
        except:
            print("❌ 无法解析错误详情JSON")
    else:
        print("✅ 保存成功")
    
    # 测试数据3 - 测试刑期为0
    print("\n3. 测试刑期为0（应该报错）...")
    test_data3 = {
        "annotation_data": {
            "案件描述": "这是一个测试案件",
            "构成原因": "构成某种犯罪的原因",
            "嫌疑人": "张三",
            "罪名": "盗窃罪",
            "基准刑_年": 0,
            "基准刑_月": 0,  # 总刑期为0应该报错
            "相似罪名": []
        }
    }
    
    response = requests.post(SAVE_ANNOTATION_URL, headers=headers, json=test_data3)
    print(f"响应状态码: {response.status_code}")
    if response.status_code != 200:
        print(f"响应内容: {response.text}")
        try:
            error_detail = response.json()
            print(f"错误详情JSON: {json.dumps(error_detail, ensure_ascii=False, indent=2)}")
        except:
            print("❌ 无法解析错误详情JSON")
    else:
        print("✅ 保存成功")
    
    # 测试数据4 - 正常数据（应该成功）
    print("\n4. 测试正常数据...")
    test_data4 = {
        "annotation_data": {
            "案件描述": "这是一个测试案件",
            "构成原因": "构成某种犯罪的原因",
            "嫌疑人": "张三",
            "罪名": "盗窃罪",
            "基准刑_年": 3,
            "基准刑_月": 6,  # 正常的月份
            "相似罪名": []
        }
    }
    
    response = requests.post(SAVE_ANNOTATION_URL, headers=headers, json=test_data4)
    print(f"响应状态码: {response.status_code}")
    if response.status_code != 200:
        print(f"响应内容: {response.text}")
        try:
            error_detail = response.json()
            print(f"错误详情JSON: {json.dumps(error_detail, ensure_ascii=False, indent=2)}")
        except:
            print("❌ 无法解析错误详情JSON")
    else:
        print("✅ 保存成功")

if __name__ == "__main__":
    test_400_error() 