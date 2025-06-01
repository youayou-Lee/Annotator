#!/usr/bin/env python3
"""
快速测试认证系统的基本功能
"""

import time
import requests
import json

def test_basic_auth():
    """测试基本认证功能"""
    base_url = "http://localhost:8000"
    
    print("🚀 开始测试认证系统基本功能...")
    
    # 等待服务器启动
    print("⏳ 等待服务器启动...")
    for i in range(10):
        try:
            response = requests.get(f"{base_url}/health", timeout=2)
            if response.status_code == 200:
                print("✅ 服务器已启动")
                break
        except:
            time.sleep(1)
    else:
        print("❌ 服务器启动失败")
        return False
    
    # 测试管理员登录
    print("\n1. 测试管理员登录...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ 管理员登录成功")
            print(f"   用户: {token_data.get('user', {}).get('username')}")
            print(f"   角色: {token_data.get('user', {}).get('role')}")
            access_token = token_data["access_token"]
        else:
            print(f"❌ 管理员登录失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 登录请求失败: {e}")
        return False
    
    # 测试获取当前用户信息
    print("\n2. 测试获取当前用户信息...")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(f"{base_url}/api/auth/me", headers=headers)
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ 获取用户信息成功")
            print(f"   ID: {user_info['id']}")
            print(f"   用户名: {user_info['username']}")
            print(f"   角色: {user_info['role']}")
        else:
            print(f"❌ 获取用户信息失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 获取用户信息请求失败: {e}")
        return False
    
    # 测试用户注册
    print("\n3. 测试用户注册...")
    register_data = {
        "username": "testuser001",
        "password": "test123456",
        "role": "annotator"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/register", json=register_data)
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ 用户注册成功")
            print(f"   用户名: {user_data['username']}")
            print(f"   角色: {user_data['role']}")
        else:
            print(f"❌ 用户注册失败: {response.text}")
            # 如果是用户已存在，不算失败
            if "已存在" in response.text:
                print("   (用户已存在，继续测试)")
            else:
                return False
    except Exception as e:
        print(f"❌ 注册请求失败: {e}")
        return False
    
    # 测试获取用户列表
    print("\n4. 测试获取用户列表...")
    try:
        response = requests.get(f"{base_url}/api/users", headers=headers)
        if response.status_code == 200:
            users = response.json()
            print(f"✅ 获取用户列表成功，共 {len(users)} 个用户")
            for user in users:
                print(f"   - {user['username']} ({user['role']})")
        else:
            print(f"❌ 获取用户列表失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 获取用户列表请求失败: {e}")
        return False
    
    print("\n🎉 基本认证功能测试通过！")
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("文书标注系统 - 认证系统快速测试")
    print("=" * 50)
    
    if test_basic_auth():
        print("\n✅ 测试完成！认证系统工作正常。")
    else:
        print("\n❌ 测试失败！请检查系统配置。") 