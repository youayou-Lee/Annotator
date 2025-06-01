#!/usr/bin/env python3
"""
测试前端登录功能
"""

import requests
import json

def test_frontend_login():
    """测试前端登录功能"""
    print("🔍 测试前端登录功能...")
    
    # 模拟前端登录请求
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        # 直接调用后端API
        response = requests.post("http://localhost:8000/api/auth/login", json=login_data)
        print(f"后端API响应状态码: {response.status_code}")
        print(f"后端API响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 后端API登录成功")
            print(f"   Token: {result.get('access_token', 'N/A')[:50]}...")
            print(f"   用户: {result.get('user', {})}")
            return True
        else:
            print("❌ 后端API登录失败")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_wrong_credentials():
    """测试错误凭据"""
    print("\n🔍 测试错误凭据...")
    
    login_data = {
        "username": "admin",
        "password": "wrongpassword"
    }
    
    try:
        response = requests.post("http://localhost:8000/api/auth/login", json=login_data)
        print(f"错误凭据响应状态码: {response.status_code}")
        print(f"错误凭据响应内容: {response.text}")
        
        if response.status_code == 401:
            print("✅ 错误凭据正确返回401")
            return True
        else:
            print("❌ 错误凭据响应异常")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_annotator_login():
    """测试标注员登录"""
    print("\n🔍 测试标注员登录...")
    
    login_data = {
        "username": "annotator",
        "password": "123456"
    }
    
    try:
        response = requests.post("http://localhost:8000/api/auth/login", json=login_data)
        print(f"标注员登录响应状态码: {response.status_code}")
        print(f"标注员登录响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 标注员登录成功")
            print(f"   用户: {result.get('user', {})}")
            return True
        else:
            print("❌ 标注员登录失败")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def main():
    print("=" * 50)
    print("🧪 前端登录功能测试")
    print("=" * 50)
    
    # 测试管理员登录
    admin_ok = test_frontend_login()
    
    # 测试错误凭据
    wrong_ok = test_wrong_credentials()
    
    # 测试标注员登录
    annotator_ok = test_annotator_login()
    
    print("\n" + "=" * 50)
    print("📊 测试结果:")
    print(f"   管理员登录: {'✅ 成功' if admin_ok else '❌ 失败'}")
    print(f"   错误凭据处理: {'✅ 正常' if wrong_ok else '❌ 异常'}")
    print(f"   标注员登录: {'✅ 成功' if annotator_ok else '❌ 失败'}")
    
    if all([admin_ok, wrong_ok, annotator_ok]):
        print("\n🎉 所有测试通过！")
        print("\n💡 现在可以在前端页面尝试登录:")
        print("   管理员: admin / admin123")
        print("   标注员: annotator / 123456")
    else:
        print("\n❌ 部分测试失败，请检查后端服务")

if __name__ == "__main__":
    main() 