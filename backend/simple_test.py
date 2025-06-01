#!/usr/bin/env python3
"""
简单测试脚本
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_login():
    """测试登录"""
    print("测试登录...")
    
    # 测试登录 - 使用JSON格式
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print(f"登录状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"登录成功，令牌: {token[:20]}...")
        return token
    else:
        print("登录失败")
        return None

def test_register():
    """测试注册"""
    print("测试注册...")
    
    register_data = {
        "username": "testuser",
        "password": "test123",
        "role": "annotator"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
    print(f"注册状态码: {response.status_code}")
    print(f"响应内容: {response.text}")

def test_files_without_auth():
    """测试无认证访问文件API"""
    print("测试无认证访问文件API...")
    
    response = requests.get(f"{BASE_URL}/api/files/")
    print(f"文件列表状态码: {response.status_code}")
    print(f"响应内容: {response.text}")

def main():
    print("开始简单测试...")
    
    # 测试服务器连接
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"服务器连接状态: {response.status_code}")
    except Exception as e:
        print(f"服务器连接失败: {e}")
        return
    
    # 测试注册
    test_register()
    
    # 测试登录
    token = test_login()
    
    # 测试无认证访问
    test_files_without_auth()
    
    if token:
        # 测试有认证访问
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/files/", headers=headers)
        print(f"有认证文件列表状态码: {response.status_code}")
        print(f"响应内容: {response.text}")

if __name__ == "__main__":
    main() 