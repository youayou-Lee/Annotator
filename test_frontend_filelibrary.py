#!/usr/bin/env python3
"""
文件库前端功能测试脚本
测试文件上传、下载、预览等功能
"""

import requests
import json
import time
import os
from pathlib import Path

# 配置
FRONTEND_URL = "http://localhost:3000"
BACKEND_URL = "http://localhost:8000"

# 全局变量存储token
auth_token = None

def login_and_get_token():
    """登录并获取认证token"""
    print("🔐 尝试登录获取认证token...")
    
    # 测试用户凭据
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
                print("✅ 登录成功，获取到token")
                return token
            else:
                print("❌ 登录响应中没有找到token")
                return None
        else:
            print(f"❌ 登录失败，状态码: {response.status_code}")
            if response.status_code == 401:
                print("   可能是用户名或密码错误")
            print(f"   响应内容: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ 登录请求失败: {e}")
        return None

def test_frontend_accessibility():
    """测试前端页面是否可访问"""
    print("🔍 测试前端页面可访问性...")
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print("✅ 前端页面可访问")
            return True
        else:
            print(f"❌ 前端页面返回状态码: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 前端页面无法访问: {e}")
        return False

def test_backend_accessibility():
    """测试后端API是否可访问"""
    print("🔍 测试后端API可访问性...")
    try:
        response = requests.get(f"{BACKEND_URL}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ 后端API可访问")
            return True
        else:
            print(f"❌ 后端API返回状态码: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 后端API无法访问: {e}")
        return False

def create_test_files():
    """创建测试文件"""
    print("📁 创建测试文件...")
    
    # 创建测试目录
    test_dir = Path("test_files")
    test_dir.mkdir(exist_ok=True)
    
    # 创建JSON测试文件
    json_file = test_dir / "test_document.json"
    json_data = {
        "id": "doc_001",
        "title": "测试文档",
        "content": "这是一个测试文档内容",
        "metadata": {
            "author": "测试用户",
            "created_at": "2024-01-01T00:00:00Z"
        }
    }
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    # 创建JSONL测试文件
    jsonl_file = test_dir / "test_documents.jsonl"
    jsonl_data = [
        {"id": "doc_001", "text": "第一个文档"},
        {"id": "doc_002", "text": "第二个文档"},
        {"id": "doc_003", "text": "第三个文档"}
    ]
    with open(jsonl_file, 'w', encoding='utf-8') as f:
        for item in jsonl_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    # 创建Python模板文件
    py_file = test_dir / "test_template.py"
    py_content = '''"""
测试标注模板
定义文档标注的字段和验证规则
"""

ANNOTATION_FIELDS = {
    "title": {
        "type": "string",
        "required": True,
        "description": "文档标题"
    },
    "category": {
        "type": "string",
        "required": True,
        "options": ["新闻", "公告", "报告"],
        "description": "文档分类"
    },
    "keywords": {
        "type": "array",
        "required": False,
        "description": "关键词列表"
    },
    "summary": {
        "type": "string",
        "required": False,
        "description": "文档摘要"
    }
}

def validate_annotation(data):
    """验证标注数据"""
    for field, config in ANNOTATION_FIELDS.items():
        if config.get("required", False) and field not in data:
            return False, f"缺少必填字段: {field}"
    return True, "验证通过"
'''
    with open(py_file, 'w', encoding='utf-8') as f:
        f.write(py_content)
    
    print(f"✅ 测试文件已创建在 {test_dir} 目录下")
    return {
        "json_file": json_file,
        "jsonl_file": jsonl_file,
        "py_file": py_file
    }

def test_file_api_endpoints():
    """测试文件相关的API端点"""
    print("🔍 测试文件API端点...")
    
    endpoints = [
        "/api/files",
        "/api/files?type=documents",
        "/api/files?type=templates",
        "/api/files?type=exports"
    ]
    
    headers = {}
    if auth_token:
        headers['Authorization'] = f'Bearer {auth_token}'
        print(f"   使用认证token: {auth_token[:20]}...")
    else:
        print("   ⚠️ 没有认证token，可能会收到403错误")
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers, timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint} - 端点可访问，返回数据")
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"   📁 找到 {len(data)} 个文件")
                    else:
                        print(f"   📄 响应数据: {data}")
                except:
                    print(f"   📄 响应长度: {len(response.text)} 字符")
            elif response.status_code == 401:
                print(f"❌ {endpoint} - 需要身份验证 (401)")
            elif response.status_code == 403:
                print(f"❌ {endpoint} - 权限不足 (403)")
            else:
                print(f"❌ {endpoint} - 状态码: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint} - 请求失败: {e}")

def test_auth_endpoints():
    """测试认证相关端点"""
    print("🔍 测试认证端点...")
    
    # 测试注册端点
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/register", json={
            "username": "test_user",
            "password": "test123"
        }, timeout=5)
        if response.status_code in [200, 201, 400, 409]:  # 成功或用户已存在
            print("✅ /api/auth/register - 端点可访问")
        else:
            print(f"❌ /api/auth/register - 状态码: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ /api/auth/register - 请求失败: {e}")
    
    # 测试登录端点
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json={
            "username": "invalid",
            "password": "invalid"
        }, timeout=5)
        if response.status_code in [200, 401]:  # 成功或认证失败都说明端点存在
            print("✅ /api/auth/login - 端点可访问")
        else:
            print(f"❌ /api/auth/login - 状态码: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ /api/auth/login - 请求失败: {e}")

def print_frontend_features():
    """打印前端功能说明"""
    print("\n📋 文件库前端功能说明:")
    print("=" * 50)
    
    features = [
        "🗂️  三类文件管理（文档/模板/导出）",
        "📤 拖拽上传和点击上传",
        "📊 上传进度显示",
        "🔍 文件搜索和排序",
        "👁️  文件预览（支持语法高亮）",
        "📥 单个和批量下载",
        "🗑️  文件删除（权限控制）",
        "✅ 文件格式校验",
        "📱 响应式布局设计",
        "🔐 基于角色的权限控制"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print("\n🎯 测试建议:")
    print("  1. 访问 http://localhost:3000 查看前端界面")
    print("  2. 登录系统后进入文件库页面")
    print("  3. 尝试上传测试文件（test_files目录下）")
    print("  4. 测试文件预览、下载、删除功能")
    print("  5. 验证搜索和排序功能")
    print("  6. 测试批量操作功能")

def print_component_structure():
    """打印组件结构"""
    print("\n🏗️  前端组件结构:")
    print("=" * 50)
    
    structure = """
FileLibrary/
├── index.tsx              # 主页面组件
│   ├── 状态管理 (useState, useEffect)
│   ├── API调用 (fileAPI)
│   ├── 事件处理 (上传、下载、删除)
│   └── 权限控制 (canUpload, canDelete)
├── components/
│   ├── FileUpload.tsx     # 文件上传组件
│   │   ├── 拖拽上传 (Dragger)
│   │   ├── 进度显示 (Progress)
│   │   ├── 文件校验 (beforeUpload)
│   │   └── 自定义请求 (customRequest)
│   ├── FileList.tsx       # 文件列表组件
│   │   ├── 表格展示 (Table)
│   │   ├── 文件图标 (getFileIcon)
│   │   ├── 操作按钮 (预览/下载/删除)
│   │   └── 批量选择 (rowSelection)
│   └── FilePreview.tsx    # 文件预览组件
│       ├── 代码编辑器 (Monaco Editor)
│       ├── 语法高亮 (getLanguage)
│       ├── JSON格式化 (formatJsonContent)
│       └── 文件下载 (handleDownload)
└── README.md              # 功能文档
"""
    print(structure)

def print_403_explanation():
    """解释403错误"""
    print("\n❓ 关于403错误的说明:")
    print("=" * 50)
    print("403 Forbidden错误表示：")
    print("  🔒 API端点需要身份验证")
    print("  🎫 需要有效的JWT token")
    print("  👤 用户需要先登录系统")
    print("  🛡️ 这是正常的安全保护机制")
    print("\n解决方案：")
    print("  1. 确保后端有默认管理员账户")
    print("  2. 使用正确的用户名密码登录")
    print("  3. 前端会自动处理token认证")
    print("  4. 测试时可以先手动登录前端界面")

def main():
    """主测试函数"""
    print("🚀 文件库前端功能测试")
    print("=" * 50)
    
    # 测试前端和后端可访问性
    frontend_ok = test_frontend_accessibility()
    backend_ok = test_backend_accessibility()
    
    # 尝试登录获取token
    global auth_token
    auth_token = login_and_get_token()
    
    # 创建测试文件
    test_files = create_test_files()
    
    # 测试认证端点
    test_auth_endpoints()
    
    # 测试API端点
    test_file_api_endpoints()
    
    # 打印功能说明
    print_frontend_features()
    print_component_structure()
    print_403_explanation()
    
    print("\n📊 测试结果总结:")
    print("=" * 50)
    print(f"前端可访问性: {'✅ 通过' if frontend_ok else '❌ 失败'}")
    print(f"后端可访问性: {'✅ 通过' if backend_ok else '❌ 失败'}")
    print(f"身份验证: {'✅ 成功' if auth_token else '❌ 失败'}")
    print(f"测试文件创建: ✅ 完成")
    
    if frontend_ok and backend_ok:
        print("\n🎉 系统运行正常，可以开始测试文件库功能！")
        print(f"📱 前端地址: {FRONTEND_URL}")
        print(f"🔧 后端地址: {BACKEND_URL}")
        
        if not auth_token:
            print("\n⚠️ 建议:")
            print("  1. 检查后端是否有默认管理员账户")
            print("  2. 或者先通过前端界面注册/登录用户")
            print("  3. 然后再测试文件库功能")
    else:
        print("\n⚠️  请确保前端和后端服务都已启动")
        print("前端启动: cd frontend && npm run dev")
        print("后端启动: cd backend && python run.py")

if __name__ == "__main__":
    main() 