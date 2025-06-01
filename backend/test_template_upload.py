#!/usr/bin/env python3
"""
模板文件上传和验证测试脚本
"""

import requests
import json

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

def test_template_upload_and_validation(token):
    """测试模板文件上传和验证"""
    print("\n=== 测试模板文件上传和验证 ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 创建有效的模板文件
    valid_template = '''# 有效的模板文件
TEMPLATE_INFO = {
    "name": "测试模板",
    "version": "1.0.0",
    "description": "这是一个测试模板"
}

ANNOTATION_FIELDS = [
    {
        "name": "title",
        "type": "string",
        "required": True,
        "description": "标题"
    },
    {
        "name": "content",
        "type": "text",
        "required": True,
        "description": "内容"
    },
    {
        "name": "category",
        "type": "select",
        "required": False,
        "description": "类别",
        "options": [
            {"value": "type1", "label": "类型1"},
            {"value": "type2", "label": "类型2"}
        ]
    }
]
'''
    
    # 测试上传有效模板
    files = {"file": ("valid_template.py", valid_template, "text/plain")}
    data = {"file_type": "templates"}
    
    response = requests.post(f"{BASE_URL}/api/files/upload", headers=headers, files=files, data=data)
    print(f"上传有效模板: {response.status_code}")
    if response.status_code == 200:
        upload_result = response.json()
        print(f"  文件ID: {upload_result['file_id']}")
        print(f"  文件路径: {upload_result['file_path']}")
        
        # 测试模板验证
        file_id = upload_result['file_id']
        response = requests.get(f"{BASE_URL}/api/files/{file_id}/validate", headers=headers)
        print(f"验证模板: {response.status_code}")
        if response.status_code == 200:
            validation_result = response.json()
            print(f"  验证结果: {'通过' if validation_result['valid'] else '失败'}")
            if validation_result['valid']:
                print(f"  模板名称: {validation_result['template_info']['name']}")
                print(f"  字段数量: {len(validation_result['annotation_fields'])}")
                for field in validation_result['annotation_fields']:
                    print(f"    - {field['name']} ({field['type']}) - {field['description']}")
        
        return file_id
    else:
        print(f"  错误: {response.text}")
    
    return None

def test_invalid_template_upload(token):
    """测试无效模板文件上传"""
    print("\n=== 测试无效模板文件上传 ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 创建无效的模板文件（缺少必需变量）
    invalid_template = '''# 无效的模板文件
# 缺少 TEMPLATE_INFO 和 ANNOTATION_FIELDS

def some_function():
    return "这不是一个有效的模板"
'''
    
    # 测试上传无效模板
    files = {"file": ("invalid_template.py", invalid_template, "text/plain")}
    data = {"file_type": "templates"}
    
    response = requests.post(f"{BASE_URL}/api/files/upload", headers=headers, files=files, data=data)
    print(f"上传无效模板: {response.status_code}")
    print(f"响应内容: {response.text}")

def test_batch_upload(token):
    """测试批量上传"""
    print("\n=== 测试批量上传 ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 创建多个测试文件
    test_files = [
        ("doc1.json", json.dumps({"title": "文档1", "content": "内容1"})),
        ("doc2.json", json.dumps({"title": "文档2", "content": "内容2"})),
        ("doc3.json", json.dumps({"title": "文档3", "content": "内容3"}))
    ]
    
    files = [("files", (filename, content, "application/json")) for filename, content in test_files]
    data = {"file_type": "documents"}
    
    response = requests.post(f"{BASE_URL}/api/files/upload/batch", headers=headers, files=files, data=data)
    print(f"批量上传: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"  成功上传: {result['total_uploaded']}")
        print(f"  失败上传: {result['total_failed']}")
        for upload in result['successful_uploads']:
            print(f"    - {upload['filename']} (ID: {upload['file_id']})")
        
        return [upload['file_id'] for upload in result['successful_uploads']]
    else:
        print(f"  错误: {response.text}")
    
    return []

def test_batch_download(token, file_ids):
    """测试批量下载"""
    print("\n=== 测试批量下载 ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    file_ids_str = ",".join(file_ids)
    response = requests.get(f"{BASE_URL}/api/files/download/batch?file_ids={file_ids_str}", headers=headers)
    print(f"批量下载: {response.status_code}")
    if response.status_code == 200:
        print(f"  Content-Type: {response.headers.get('content-type')}")
        print(f"  文件大小: {len(response.content)} bytes")
    else:
        print(f"  错误: {response.text}")

def main():
    """主测试函数"""
    print("开始模板文件测试...")
    
    # 获取认证令牌
    token = get_auth_token()
    if not token:
        print("无法获取认证令牌，测试终止")
        return
    
    print(f"认证成功，令牌: {token[:20]}...")
    
    # 测试有效模板上传和验证
    template_file_id = test_template_upload_and_validation(token)
    
    # 测试无效模板上传
    test_invalid_template_upload(token)
    
    # 测试批量上传
    batch_file_ids = test_batch_upload(token)
    
    # 测试批量下载
    if batch_file_ids:
        test_batch_download(token, batch_file_ids)
    
    # 清理测试文件
    headers = {"Authorization": f"Bearer {token}"}
    all_file_ids = [template_file_id] + batch_file_ids if template_file_id else batch_file_ids
    
    for file_id in all_file_ids:
        if file_id:
            response = requests.delete(f"{BASE_URL}/api/files/{file_id}", headers=headers)
            print(f"删除文件 {file_id}: {response.status_code}")
    
    print("\n模板文件测试完成！")

if __name__ == "__main__":
    main() 