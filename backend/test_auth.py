#!/usr/bin/env python3
"""
认证系统测试脚本
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_auth_system():
    """测试认证系统"""
    print("🚀 开始测试认证系统...")
    
    # 1. 测试健康检查
    print("\n1. 测试健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ 健康检查通过")
        else:
            print("❌ 健康检查失败")
            return False
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        return False
    
    # 2. 测试用户注册
    print("\n2. 测试用户注册...")
    register_data = {
        "username": "testuser",
        "password": "test123456",
        "role": "annotator"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ 用户注册成功: {user_data['username']}")
        else:
            print(f"❌ 用户注册失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 注册请求失败: {e}")
        return False
    
    # 3. 测试用户登录
    print("\n3. 测试用户登录...")
    login_data = {
        "username": "testuser",
        "password": "test123456"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            print(f"✅ 用户登录成功，获得令牌")
        else:
            print(f"❌ 用户登录失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 登录请求失败: {e}")
        return False
    
    # 4. 测试获取当前用户信息
    print("\n4. 测试获取当前用户信息...")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ 获取用户信息成功: {user_info['username']} ({user_info['role']})")
        else:
            print(f"❌ 获取用户信息失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 获取用户信息请求失败: {e}")
        return False
    
    # 5. 测试管理员登录
    print("\n5. 测试管理员登录...")
    admin_login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=admin_login_data)
        if response.status_code == 200:
            admin_token_data = response.json()
            admin_access_token = admin_token_data["access_token"]
            print(f"✅ 管理员登录成功")
        else:
            print(f"❌ 管理员登录失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 管理员登录请求失败: {e}")
        return False
    
    # 6. 测试获取用户列表（需要管理员权限）
    print("\n6. 测试获取用户列表...")
    admin_headers = {"Authorization": f"Bearer {admin_access_token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/users", headers=admin_headers)
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
    
    # 7. 测试普通用户访问用户列表（应该失败）
    print("\n7. 测试普通用户访问用户列表...")
    try:
        response = requests.get(f"{BASE_URL}/api/users", headers=headers)
        if response.status_code == 403:
            print("✅ 权限控制正常，普通用户无法访问用户列表")
        else:
            print(f"❌ 权限控制异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 权限测试请求失败: {e}")
        return False
    
    # 8. 测试令牌刷新
    print("\n8. 测试令牌刷新...")
    try:
        response = requests.post(f"{BASE_URL}/api/auth/refresh", headers=headers)
        if response.status_code == 200:
            new_token_data = response.json()
            print("✅ 令牌刷新成功")
        else:
            print(f"❌ 令牌刷新失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 令牌刷新请求失败: {e}")
        return False
    
    print("\n🎉 所有认证系统测试通过！")
    return True


def test_error_cases():
    """测试错误情况"""
    print("\n🔍 测试错误情况...")
    
    # 测试错误的登录凭据
    print("\n1. 测试错误的登录凭据...")
    wrong_login_data = {
        "username": "wronguser",
        "password": "wrongpassword"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=wrong_login_data)
        if response.status_code == 401:
            print("✅ 错误凭据被正确拒绝")
        else:
            print(f"❌ 错误凭据处理异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 错误凭据测试失败: {e}")
    
    # 测试重复用户名注册
    print("\n2. 测试重复用户名注册...")
    duplicate_register_data = {
        "username": "testuser",  # 已存在的用户名
        "password": "test123456",
        "role": "annotator"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=duplicate_register_data)
        if response.status_code == 400:
            print("✅ 重复用户名被正确拒绝")
        else:
            print(f"❌ 重复用户名处理异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 重复用户名测试失败: {e}")
    
    # 测试无效令牌
    print("\n3. 测试无效令牌...")
    invalid_headers = {"Authorization": "Bearer invalid_token"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=invalid_headers)
        if response.status_code == 401:
            print("✅ 无效令牌被正确拒绝")
        else:
            print(f"❌ 无效令牌处理异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 无效令牌测试失败: {e}")


if __name__ == "__main__":
    print("=" * 50)
    print("文书标注系统 - 认证系统测试")
    print("=" * 50)
    
    # 基本功能测试
    if test_auth_system():
        # 错误情况测试
        test_error_cases()
        print("\n✅ 所有测试完成！")
    else:
        print("\n❌ 基本功能测试失败，请检查系统配置")
        sys.exit(1) 