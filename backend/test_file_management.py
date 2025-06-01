#!/usr/bin/env python3
"""
文件管理功能测试脚本
"""

import requests
import json
import os
from pathlib import Path

# 配置
BASE_URL = "http://localhost:8000"
TEST_USERNAME = "admin"
TEST_PASSWORD = "admin123"

def get_auth_token():
    """获取认证令牌"""
    login_data = {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"登录失败: {response.text}")
        return None

def test_file_list(token):
    """测试文件列表功能"""
    print("\n=== 测试文件列表功能 ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 测试获取所有文件
    response = requests.get(f"{BASE_URL}/api/files/", headers=headers)
    print(f"获取所有文件: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"文件总数: {data['total']}")
        for file_info in data['files']:
            print(f"  - {file_info['filename']} ({file_info['file_type']}) - {file_info['file_size']} bytes")
    
    # 测试按类型筛选
    for file_type in ["documents", "templates", "exports"]:
        response = requests.get(f"{BASE_URL}/api/files/?file_type={file_type}", headers=headers)
        print(f"获取{file_type}文件: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  {file_type}文件数: {data['total']}")

def test_file_upload(token):
    """测试文件上传功能"""
    print("\n=== 测试文件上传功能 ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 创建测试文件
    test_json_content = {
        "test": "这是一个测试JSON文件",
        "data": [1, 2, 3, 4, 5]
    }
    
    test_py_content = '''# 测试模板文件
TEMPLATE_INFO = {
    "name": "测试模板",
    "version": "1.0.0",
    "description": "这是一个测试模板"
}

ANNOTATION_FIELDS = [
    {
        "name": "test_field",
        "type": "string",
        "required": True,
        "description": "测试字段"
    }
]
'''
    
    # 测试上传JSON文档
    files = {"file": ("test_document.json", json.dumps(test_json_content, ensure_ascii=False), "application/json")}
    data = {"file_type": "documents"}
    
    response = requests.post(f"{BASE_URL}/api/files/upload", headers=headers, files=files, data=data)
    print(f"上传JSON文档: {response.status_code}")
    if response.status_code == 200:
        upload_result = response.json()
        print(f"  文件ID: {upload_result['file_id']}")
        print(f"  文件路径: {upload_result['file_path']}")
        return upload_result['file_id']
    else:
        print(f"  错误: {response.text}")
    
    # 测试上传Python模板
    files = {"file": ("test_template.py", test_py_content, "text/plain")}
    data = {"file_type": "templates"}
    
    response = requests.post(f"{BASE_URL}/api/files/upload", headers=headers, files=files, data=data)
    print(f"上传Python模板: {response.status_code}")
    if response.status_code == 200:
        upload_result = response.json()
        print(f"  文件ID: {upload_result['file_id']}")
        print(f"  文件路径: {upload_result['file_path']}")
        return upload_result['file_id']
    else:
        print(f"  错误: {response.text}")
    
    return None

def test_file_preview(token, file_id):
    """测试文件预览功能"""
    print(f"\n=== 测试文件预览功能 (文件ID: {file_id}) ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/api/files/{file_id}/preview", headers=headers)
    print(f"预览文件: {response.status_code}")
    if response.status_code == 200:
        preview_data = response.json()
        print(f"  文件名: {preview_data['filename']}")
        print(f"  文件类型: {preview_data['file_type']}")
        print(f"  文件大小: {preview_data['file_size']} bytes")
        print(f"  内容预览: {preview_data['content'][:200]}...")
    else:
        print(f"  错误: {response.text}")

def test_template_validation(token, file_id):
    """测试模板验证功能"""
    print(f"\n=== 测试模板验证功能 (文件ID: {file_id}) ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/api/files/{file_id}/validate", headers=headers)
    print(f"验证模板: {response.status_code}")
    if response.status_code == 200:
        validation_result = response.json()
        print(f"  验证结果: {'通过' if validation_result['valid'] else '失败'}")
        if validation_result['valid']:
            print(f"  模板名称: {validation_result['template_info']['name']}")
            print(f"  字段数量: {len(validation_result['annotation_fields'])}")
        else:
            print(f"  错误信息: {validation_result['error']}")
    else:
        print(f"  错误: {response.text}")

def test_file_download(token, file_id):
    """测试文件下载功能"""
    print(f"\n=== 测试文件下载功能 (文件ID: {file_id}) ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/api/files/{file_id}/download", headers=headers)
    print(f"下载文件: {response.status_code}")
    if response.status_code == 200:
        print(f"  Content-Type: {response.headers.get('content-type')}")
        print(f"  Content-Length: {response.headers.get('content-length')} bytes")
        print(f"  文件内容长度: {len(response.content)} bytes")
    else:
        print(f"  错误: {response.text}")

def test_file_delete(token, file_id):
    """测试文件删除功能"""
    print(f"\n=== 测试文件删除功能 (文件ID: {file_id}) ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.delete(f"{BASE_URL}/api/files/{file_id}", headers=headers)
    print(f"删除文件: {response.status_code}")
    if response.status_code == 200:
        delete_result = response.json()
        print(f"  删除结果: {'成功' if delete_result['success'] else '失败'}")
        print(f"  消息: {delete_result['message']}")
    else:
        print(f"  错误: {response.text}")

def test_my_files(token):
    """测试我的文件功能"""
    print("\n=== 测试我的文件功能 ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/api/files/my-files", headers=headers)
    print(f"获取我的文件: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"我的文件总数: {data['total']}")
        for file_info in data['files']:
            print(f"  - {file_info['filename']} ({file_info['file_type']}) - {file_info['file_size']} bytes")
    else:
        print(f"  错误: {response.text}")

def main():
    """主测试函数"""
    print("开始文件管理功能测试...")
    
    # 获取认证令牌
    token = get_auth_token()
    if not token:
        print("无法获取认证令牌，测试终止")
        return
    
    print(f"认证成功，令牌: {token[:20]}...")
    
    # 测试文件列表
    test_file_list(token)
    
    # 测试文件上传
    uploaded_file_id = test_file_upload(token)
    
    if uploaded_file_id:
        # 测试文件预览
        test_file_preview(token, uploaded_file_id)
        
        # 测试文件下载
        test_file_download(token, uploaded_file_id)
        
        # 测试我的文件
        test_my_files(token)
        
        # 测试文件删除
        test_file_delete(token, uploaded_file_id)
    
    print("\n文件管理功能测试完成！")

if __name__ == "__main__":
    main() 