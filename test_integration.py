#!/usr/bin/env python3
"""
前后端集成测试脚本
"""

import requests
import time
import webbrowser
from urllib.parse import urljoin

def test_backend():
    """测试后端服务"""
    print("🔍 测试后端服务...")
    
    try:
        # 测试健康检查
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务运行正常")
            return True
        else:
            print(f"❌ 后端服务状态异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到后端服务: {e}")
        return False

def test_frontend():
    """测试前端服务"""
    print("🔍 测试前端服务...")
    
    try:
        # 测试前端页面
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ 前端服务运行正常")
            return True
        else:
            print(f"❌ 前端服务状态异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到前端服务: {e}")
        return False

def test_auth_api():
    """测试认证API"""
    print("🔍 测试认证API...")
    
    # 测试管理员登录
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post("http://localhost:8000/api/auth/login", json=login_data, timeout=5)
        if response.status_code == 200:
            result = response.json()
            print("✅ 管理员登录成功")
            print(f"   用户: {result['user']['username']}")
            print(f"   角色: {result['user']['role']}")
            return True
        else:
            print(f"❌ 管理员登录失败: {response.status_code}")
            print(f"   错误: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 登录API请求失败: {e}")
        return False

def test_cors():
    """测试CORS配置"""
    print("🔍 测试CORS配置...")
    
    headers = {
        'Origin': 'http://localhost:3000',
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type'
    }
    
    try:
        response = requests.options("http://localhost:8000/api/auth/login", headers=headers, timeout=5)
        if response.status_code in [200, 204]:
            print("✅ CORS配置正常")
            return True
        else:
            print(f"❌ CORS配置异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ CORS测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("🚀 文书标注系统集成测试")
    print("=" * 50)
    
    # 测试后端
    backend_ok = test_backend()
    print()
    
    # 测试前端
    frontend_ok = test_frontend()
    print()
    
    # 测试认证API
    auth_ok = test_auth_api()
    print()
    
    # 测试CORS
    cors_ok = test_cors()
    print()
    
    # 总结
    print("=" * 50)
    print("📊 测试结果总结:")
    print(f"   后端服务: {'✅ 正常' if backend_ok else '❌ 异常'}")
    print(f"   前端服务: {'✅ 正常' if frontend_ok else '❌ 异常'}")
    print(f"   认证API: {'✅ 正常' if auth_ok else '❌ 异常'}")
    print(f"   CORS配置: {'✅ 正常' if cors_ok else '❌ 异常'}")
    
    if all([backend_ok, frontend_ok, auth_ok, cors_ok]):
        print("\n🎉 所有测试通过！系统运行正常")
        print("\n📱 可以访问以下地址:")
        print("   前端应用: http://localhost:3000")
        print("   后端API: http://localhost:8000/docs")
        print("\n🔑 演示账户:")
        print("   管理员: admin / admin123")
        print("   标注员: annotator / 123456")
        
        # 询问是否打开浏览器
        try:
            choice = input("\n是否打开浏览器访问前端应用? (y/n): ").lower().strip()
            if choice in ['y', 'yes', '是']:
                print("🌐 正在打开浏览器...")
                webbrowser.open("http://localhost:3000")
        except KeyboardInterrupt:
            print("\n👋 测试结束")
    else:
        print("\n❌ 部分测试失败，请检查服务状态")
        if not backend_ok:
            print("   请确保后端服务已启动: cd backend && python run.py")
        if not frontend_ok:
            print("   请确保前端服务已启动: cd frontend && npm run dev")

if __name__ == "__main__":
    main() 