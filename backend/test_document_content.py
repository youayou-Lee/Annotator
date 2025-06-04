#!/usr/bin/env python3
"""
测试文档内容API是否返回标注结果
"""

import requests
import json

# 测试API的基本配置
BASE_URL = "http://localhost:8000"

def get_auth_token():
    """获取认证token"""
    print("正在获取认证token...")
    
    # 尝试使用管理员账户登录
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            print("✅ 管理员登录成功，获得令牌")
            return access_token
        else:
            print(f"❌ 登录失败: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 登录请求失败: {str(e)}")
        return None

def test_document_content_api():
    """测试文档内容API是否返回标注结果"""
    
    # 获取认证token
    token = get_auth_token()
    if not token:
        print("无法获取认证token，测试终止")
        return False
    
    # 使用存在的任务ID和文档ID
    task_id = "task_f946d1d6"
    document_id = "doc_35774d2b"
    
    # 构建API URL
    url = f"{BASE_URL}/api/annotations/{task_id}/documents/{document_id}/content"
    
    # 设置认证头
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n测试API: {url}")
    
    try:
        response = requests.get(url, headers=headers)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API响应成功!")
            print(f"文档ID: {data['document_id']}")
            print(f"内容类型: {type(data['content'])}")
            
            # 检查内容是否来自标注结果
            if isinstance(data['content'], dict):
                if 'items' in data['content']:
                    items = data['content']['items']
                    if isinstance(items, list) and len(items) > 0:
                        first_item = items[0]
                        print(f"内容项数量: {len(items)}")
                        print(f"第一项结构: {list(first_item.keys()) if isinstance(first_item, dict) else type(first_item)}")
                        
                        # 检查是否包含标注后的字段
                        if isinstance(first_item, dict):
                            if 'criminal_names' in first_item and 'range' in first_item:
                                print("🎉 成功！API返回的是标注结果数据")
                                print(f"第一条数据: {first_item.get('id', 'N/A')} - {first_item.get('criminal_names', [])}")
                                print(f"刑期范围: {len(first_item.get('range', []))} 项")
                                return True
                            else:
                                print("⚠️  返回的是数组数据，但不是预期的标注结果格式")
                                print(f"第一项包含的字段: {list(first_item.keys())}")
                else:
                    print("⚠️  返回的内容不包含 'items' 字段")
                    print(f"内容结构: {list(data['content'].keys())}")
            else:
                print(f"⚠️  返回的内容不是字典格式: {type(data['content'])}")
            
            print("\n📄 API返回的内容预览:")
            formatted_content = data.get('formatted_content', '')
            preview = formatted_content[:500] + '...' if len(formatted_content) > 500 else formatted_content
            print(preview)
            
        elif response.status_code == 404:
            print("❌ 文档或任务不存在")
        elif response.status_code == 403:
            print("❌ 没有权限访问此文档")
        else:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
    
    return False

def test_health_check():
    """测试健康检查"""
    print("检查后端服务状态...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ 后端服务正常运行")
            return True
        else:
            print(f"❌ 后端服务状态异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到后端服务: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 测试文档内容API是否返回标注结果")
    print("=" * 60)
    
    # 先检查服务状态
    if not test_health_check():
        print("后端服务不可用，测试终止")
        exit(1)
    
    # 测试文档内容API
    success = test_document_content_api()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 测试成功！文档内容API现在返回标注结果")
    else:
        print("❌ 测试失败！需要检查API实现")
    print("=" * 60) 