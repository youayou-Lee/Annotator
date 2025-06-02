#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的标注任务详情页面功能测试
"""

import json
import requests
import time
from pathlib import Path

# API基础URL
BASE_URL = "http://localhost:8000"

def login_and_get_token():
    """登录并获取访问令牌"""
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"登录失败: {response.text}")
        return None

def get_headers(token):
    """获取请求头"""
    return {"Authorization": f"Bearer {token}"}

def create_admin_task(headers):
    """创建分配给admin的测试任务"""
    print("📝 创建测试任务...")
    
    # 获取文档文件
    response = requests.get(f"{BASE_URL}/api/files/", headers=headers, params={"file_type": "documents"})
    if response.status_code != 200:
        print(f"❌ 获取文档文件失败: {response.text}")
        return None
    
    document_files = response.json().get("files", [])
    if not document_files:
        print("❌ 没有可用的文档文件")
        return None
    
    # 获取模板文件
    response = requests.get(f"{BASE_URL}/api/files/", headers=headers, params={"file_type": "templates"})
    template_files = []
    if response.status_code == 200:
        template_files = response.json().get("files", [])
    
    # 创建任务
    task_data = {
        "name": "完整测试任务",
        "description": "用于测试标注任务详情页面的完整功能",
        "assignee_id": "user_0b072cec",  # admin用户ID
        "documents": [doc["file_path"] for doc in document_files[:2]],
        "template_path": template_files[0]["file_path"] if template_files else None
    }
    
    response = requests.post(f"{BASE_URL}/api/tasks/", headers=headers, json=task_data)
    if response.status_code == 200:
        task = response.json()
        print(f"✅ 任务创建成功: {task['id']}")
        return task["id"]
    else:
        print(f"❌ 任务创建失败: {response.text}")
        return None

def test_complete_annotation_workflow():
    """测试完整的标注工作流程"""
    print("🚀 开始完整的标注功能测试...")
    
    # 1. 登录
    print("\n1. 登录...")
    token = login_and_get_token()
    if not token:
        print("❌ 登录失败，测试终止")
        return
    print("✅ 登录成功")
    
    headers = get_headers(token)
    
    # 2. 创建测试任务
    task_id = create_admin_task(headers)
    if not task_id:
        print("❌ 无法创建测试任务，测试终止")
        return
    
    # 3. 测试获取任务文档列表
    print(f"\n3. 测试获取任务文档列表...")
    response = requests.get(f"{BASE_URL}/api/annotations/{task_id}/documents", headers=headers)
    if response.status_code == 200:
        documents_data = response.json()
        print(f"✅ 获取文档列表成功")
        print(f"   - 总文档数: {documents_data['total_count']}")
        print(f"   - 已完成: {documents_data['completed_count']}")
        print(f"   - 进行中: {documents_data['in_progress_count']}")
        print(f"   - 待开始: {documents_data['pending_count']}")
        
        if documents_data['documents']:
            document_id = documents_data['documents'][0]['document_id']
            document_name = documents_data['documents'][0]['document_name']
            print(f"   - 第一个文档: {document_name} (ID: {document_id})")
        else:
            print("❌ 任务中没有文档")
            return
    else:
        print(f"❌ 获取文档列表失败: {response.text}")
        return
    
    # 4. 测试获取文档内容
    print(f"\n4. 测试获取文档内容...")
    response = requests.get(f"{BASE_URL}/api/annotations/{task_id}/documents/{document_id}/content", headers=headers)
    if response.status_code == 200:
        content_data = response.json()
        print("✅ 获取文档内容成功")
        print(f"   - 文档ID: {content_data['document_id']}")
        print(f"   - 内容长度: {len(content_data['formatted_content'])} 字符")
        print(f"   - 内容预览: {content_data['formatted_content'][:100]}...")
    else:
        print(f"❌ 获取文档内容失败: {response.text}")
    
    # 5. 测试获取表单配置
    print(f"\n5. 测试获取表单配置...")
    response = requests.get(f"{BASE_URL}/api/annotations/{task_id}/documents/{document_id}/form-config", headers=headers)
    if response.status_code == 200:
        form_config = response.json()
        print("✅ 获取表单配置成功")
        print(f"   - 字段数量: {len(form_config['fields'])}")
        print(f"   - 模板信息: {form_config['template_info']}")
        
        if form_config['fields']:
            print("   - 字段列表:")
            for field in form_config['fields'][:5]:  # 显示前5个字段
                print(f"     * {field['path']} ({field['field_type']}) - 必填: {field['required']}")
                if field.get('description'):
                    print(f"       描述: {field['description']}")
    else:
        print(f"❌ 获取表单配置失败: {response.text}")
    
    # 6. 测试获取标注数据
    print(f"\n6. 测试获取标注数据...")
    response = requests.get(f"{BASE_URL}/api/annotations/{task_id}/documents/{document_id}/annotation", headers=headers)
    if response.status_code == 200:
        annotation_data = response.json()
        print("✅ 获取标注数据成功")
        print(f"   - 状态: {annotation_data['status']}")
        print(f"   - 标注员ID: {annotation_data.get('annotator_id', 'N/A')}")
        print(f"   - 更新时间: {annotation_data.get('updated_at', 'N/A')}")
        print(f"   - 标注数据: {annotation_data.get('annotation_data', {})}")
    else:
        print(f"❌ 获取标注数据失败: {response.text}")
    
    # 7. 测试保存标注数据
    print(f"\n7. 测试保存标注数据...")
    test_annotation_data = {
        "annotation_data": {
            "article_title": "测试新闻标题",
            "article_summary": "这是一个测试新闻的摘要，用于验证标注功能是否正常工作。",
            "primary_category": "technology",
            "overall_sentiment": "positive",
            "sentiment_confidence": 0.85,
            "content_quality": 8,
            "factual_accuracy": 9,
            "readability": 7,
            "contains_statistics": True,
            "timestamp": time.time()
        },
        "status": "in_progress"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/annotations/{task_id}/documents/{document_id}/annotation",
        headers=headers,
        json=test_annotation_data
    )
    if response.status_code == 200:
        saved_annotation = response.json()
        print("✅ 保存标注数据成功")
        print(f"   - 状态: {saved_annotation['status']}")
        print(f"   - 更新时间: {saved_annotation['updated_at']}")
    else:
        print(f"❌ 保存标注数据失败: {response.text}")
    
    # 8. 测试获取任务进度
    print(f"\n8. 测试获取任务进度...")
    response = requests.get(
        f"{BASE_URL}/api/annotations/{task_id}/progress",
        headers=headers,
        params={"current_document_id": document_id}
    )
    if response.status_code == 200:
        progress_data = response.json()
        print("✅ 获取任务进度成功")
        print(f"   - 总文档数: {progress_data['total_documents']}")
        print(f"   - 已完成: {progress_data['completed_documents']}")
        print(f"   - 进行中: {progress_data['in_progress_documents']}")
        print(f"   - 待开始: {progress_data['pending_documents']}")
        print(f"   - 完成百分比: {progress_data['completion_percentage']}%")
        
        if progress_data['current_document_progress']:
            current_doc = progress_data['current_document_progress']
            print(f"   - 当前文档状态: {current_doc['status']}")
            print(f"   - 有标注数据: {current_doc['has_data']}")
    else:
        print(f"❌ 获取任务进度失败: {response.text}")
    
    # 9. 测试提交标注
    print(f"\n9. 测试提交标注...")
    submit_data = {
        "annotation_data": {
            "article_title": "最终测试新闻标题",
            "article_summary": "这是最终提交的测试新闻摘要，包含了完整的标注信息。",
            "primary_category": "technology",
            "secondary_categories": ["ai", "innovation"],
            "overall_sentiment": "positive",
            "sentiment_confidence": 0.92,
            "content_quality": 9,
            "factual_accuracy": 9,
            "readability": 8,
            "main_entities": [
                {"name": "AI技术", "type": "technology", "confidence": 0.95},
                {"name": "创新", "type": "concept", "confidence": 0.88}
            ],
            "keywords": [
                {"word": "人工智能", "relevance": 0.95},
                {"word": "技术创新", "relevance": 0.87}
            ],
            "contains_statistics": True,
            "statistics_verified": True,
            "completed_at": time.time(),
            "quality_score": 95
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/annotations/{task_id}/documents/{document_id}/submit",
        headers=headers,
        json=submit_data
    )
    if response.status_code == 200:
        submitted_annotation = response.json()
        print("✅ 提交标注成功")
        print(f"   - 状态: {submitted_annotation['status']}")
        print(f"   - 更新时间: {submitted_annotation['updated_at']}")
    else:
        print(f"❌ 提交标注失败: {response.text}")
    
    # 10. 再次检查任务进度
    print(f"\n10. 再次检查任务进度...")
    response = requests.get(f"{BASE_URL}/api/annotations/{task_id}/progress", headers=headers)
    if response.status_code == 200:
        progress_data = response.json()
        print("✅ 获取更新后的任务进度成功")
        print(f"   - 完成百分比: {progress_data['completion_percentage']}%")
        print(f"   - 已完成文档数: {progress_data['completed_documents']}")
    else:
        print(f"❌ 获取更新后的任务进度失败: {response.text}")
    
    # 11. 测试文档列表过滤
    print(f"\n11. 测试文档列表过滤功能...")
    statuses = ["pending", "in_progress", "completed"]
    
    for status in statuses:
        response = requests.get(
            f"{BASE_URL}/api/annotations/{task_id}/documents",
            headers=headers,
            params={"status_filter": status}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 过滤 {status} 状态: 找到 {data['total_count']} 个文档")
        else:
            print(f"   ❌ 过滤 {status} 状态失败: {response.text}")
    
    print("\n🎉 标注任务详情页面完整功能测试完成！")
    print(f"📋 测试任务ID: {task_id}")
    
    return task_id

if __name__ == "__main__":
    try:
        test_complete_annotation_workflow()
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc() 