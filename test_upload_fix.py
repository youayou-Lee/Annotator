#!/usr/bin/env python3
"""
文件上传修复验证测试脚本
"""

import requests
import json
import os
from pathlib import Path

# 配置
BACKEND_URL = "http://localhost:8000"

def test_login_and_get_token():
    """登录并获取认证token"""
    print("🔐 登录获取认证token...")
    
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            if token:
                print("✅ 登录成功")
                return token
            else:
                print("❌ 登录响应中没有找到token")
                return None
        else:
            print(f"❌ 登录失败，状态码: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ 登录请求失败: {e}")
        return None

def test_file_upload(token):
    """测试文件上传功能"""
    print("📤 测试文件上传功能...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # 创建测试文件
    test_file_content = {
        "id": "test_001",
        "title": "测试文档",
        "content": "这是一个测试文档内容"
    }
    
    test_file_path = Path("test_upload.json")
    with open(test_file_path, 'w', encoding='utf-8') as f:
        json.dump(test_file_content, f, ensure_ascii=False, indent=2)
    
    try:
        # 测试上传文档文件
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_upload.json', f, 'application/json')}
            data = {'file_type': 'documents'}
            
            response = requests.post(
                f"{BACKEND_URL}/api/files/upload",
                headers=headers,
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 文件上传成功")
                print(f"   文件ID: {result.get('file_id')}")
                print(f"   文件名: {result.get('filename')}")
                print(f"   消息: {result.get('message')}")
                return result.get('file_id')
            else:
                print(f"❌ 文件上传失败，状态码: {response.status_code}")
                print(f"   响应内容: {response.text}")
                return None
                
    except requests.exceptions.RequestException as e:
        print(f"❌ 文件上传请求失败: {e}")
        return None
    finally:
        # 清理测试文件
        if test_file_path.exists():
            test_file_path.unlink()

def test_file_list(token):
    """测试文件列表功能"""
    print("📋 测试文件列表功能...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/files?type=documents", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ 文件列表获取成功")
            print(f"   文件数量: {data.get('total', 0)}")
            if data.get('files'):
                for file_info in data['files'][:3]:  # 只显示前3个
                    print(f"   - {file_info.get('filename')} ({file_info.get('file_size')} bytes)")
            return True
        else:
            print(f"❌ 文件列表获取失败，状态码: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 文件列表请求失败: {e}")
        return False

def test_file_delete(token, file_id):
    """测试文件删除功能"""
    if not file_id:
        print("⏭️  跳过文件删除测试（没有文件ID）")
        return True
        
    print("🗑️  测试文件删除功能...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        response = requests.delete(f"{BACKEND_URL}/api/files/{file_id}", headers=headers, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("✅ 文件删除成功")
            print(f"   消息: {result.get('message')}")
            return True
        else:
            print(f"❌ 文件删除失败，状态码: {response.status_code}")
            print(f"   响应内容: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 文件删除请求失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 文件上传修复验证测试")
    print("=" * 50)
    
    # 测试登录
    token = test_login_and_get_token()
    if not token:
        print("❌ 无法获取认证token，测试终止")
        return
    
    # 测试文件上传
    file_id = test_file_upload(token)
    
    # 测试文件列表
    list_success = test_file_list(token)
    
    # 测试文件删除
    delete_success = test_file_delete(token, file_id)
    
    print("\n📊 测试结果总结:")
    print("=" * 50)
    print(f"登录认证: ✅ 成功")
    print(f"文件上传: {'✅ 成功' if file_id else '❌ 失败'}")
    print(f"文件列表: {'✅ 成功' if list_success else '❌ 失败'}")
    print(f"文件删除: {'✅ 成功' if delete_success else '❌ 失败'}")
    
    if file_id and list_success:
        print("\n🎉 文件上传功能修复成功！")
        print("💡 现在可以在前端测试文件上传功能了")
    else:
        print("\n⚠️  还有问题需要解决")

if __name__ == "__main__":
    main() 