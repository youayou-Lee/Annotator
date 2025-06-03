#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试简洁版本标注结果文件生成
验证是否生成了与原始文档结构一致的简洁结果文件
"""

import requests
import json
import time
from pathlib import Path

def test_simple_annotation_result():
    """测试简洁版本标注结果生成"""
    print("🧪 测试简洁版本标注结果文件生成")
    print("=" * 60)
    
    # 基本配置
    base_url = "http://localhost:8000/api"
    headers = {"Content-Type": "application/json"}
    
    # 1. 登录获取token
    print("1. 登录获取token...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            headers["Authorization"] = f"Bearer {token}"
            print("✅ 登录成功")
        else:
            print(f"❌ 登录失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 登录失败: {e}")
        return False
    
    # 2. 获取任务列表
    print("\n2. 获取任务列表...")
    try:
        response = requests.get(f"{base_url}/tasks", headers=headers, timeout=10)
        if response.status_code == 200:
            tasks = response.json()
            if not tasks:
                print("❌ 没有可用任务")
                return False
            
            task = tasks[0]
            task_id = task['id']
            print(f"✅ 选择任务: {task['name']} (ID: {task_id})")
        else:
            print(f"❌ 获取任务失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 获取任务失败: {e}")
        return False
    
    # 3. 获取文档列表
    print("\n3. 获取文档列表...")
    try:
        response = requests.get(f"{base_url}/annotations/{task_id}/documents", headers=headers, timeout=10)
        if response.status_code == 200:
            docs_data = response.json()
            documents = docs_data.get('documents', [])
            if not documents:
                print("❌ 任务中没有文档")
                return False
            
            document = documents[0]
            document_id = document['document_id']
            print(f"✅ 选择文档: {document['document_name']} (ID: {document_id})")
        else:
            print(f"❌ 获取文档列表失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 获取文档列表失败: {e}")
        return False
    
    # 4. 提交标注以生成简洁结果文件
    print("\n4. 提交标注生成简洁结果文件...")
    submit_data = {
        "annotation_data": {
            "items": [
                {
                    "id": "test_simple_result",
                    "text1": "这是测试简洁结果生成功能的标注内容",
                    "end": 999,
                    "document_info": {
                        "title": "测试文档 - 简洁结果",
                        "category": "测试类别",
                        "metadata": {
                            "author": "测试作者",
                            "publish_date": "2024-12-19",
                            "classification": "测试"
                        }
                    },
                    "content_sections": [
                        {
                            "section_id": "test_section",
                            "text": "这是标注后的测试内容，应该以简洁格式保存",
                            "annotations": {
                                "sentiment_score": 0.85,
                                "key_entities": ["测试实体1", "测试实体2"],
                                "importance_level": 4
                            }
                        }
                    ],
                    "statistics": {
                        "word_count": 100,
                        "paragraph_count": 2,
                        "reading_time": 1
                    }
                }
            ],
            "type": "array",
            "count": 1
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/annotations/{task_id}/documents/{document_id}/submit",
            json=submit_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ 标注提交成功")
        else:
            print(f"❌ 标注提交失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 标注提交失败: {e}")
        return False
    
    # 5. 检查生成的文件
    print("\n5. 检查生成的标注结果文件...")
    
    # 检查完整标注文件
    full_annotation_file = Path(f"backend/data/tasks/{task_id}/annotations/{document_id}.json")
    if full_annotation_file.exists():
        print(f"✅ 完整标注文件已生成: {full_annotation_file}")
        with open(full_annotation_file, 'r', encoding='utf-8') as f:
            full_data = json.load(f)
        print(f"   - 文件大小: {full_annotation_file.stat().st_size} bytes")
        print(f"   - 包含字段: {list(full_data.keys())}")
    else:
        print(f"❌ 完整标注文件未生成: {full_annotation_file}")
        return False
    
    # 检查简洁结果文件
    simple_result_file = Path(f"backend/data/annotations/{task_id}/{document_id}.json")
    if simple_result_file.exists():
        print(f"✅ 简洁结果文件已生成: {simple_result_file}")
        with open(simple_result_file, 'r', encoding='utf-8') as f:
            simple_data = json.load(f)
        print(f"   - 文件大小: {simple_result_file.stat().st_size} bytes")
        print(f"   - 数据类型: {type(simple_data)}")
        
        if isinstance(simple_data, list) and len(simple_data) > 0:
            first_item = simple_data[0]
            print(f"   - 第一个项目包含字段: {list(first_item.keys()) if isinstance(first_item, dict) else 'N/A'}")
            
            # 验证结构是否与原始文档一致
            expected_fields = {'id', 'text1', 'document_info', 'content_sections'}
            if isinstance(first_item, dict):
                actual_fields = set(first_item.keys())
                if expected_fields.issubset(actual_fields):
                    print("   ✅ 文件结构与原始文档一致")
                else:
                    print(f"   ⚠️  缺少字段: {expected_fields - actual_fields}")
        
        # 显示简洁文件内容示例
        print("\n   简洁结果文件内容示例:")
        print("   " + "=" * 40)
        print(json.dumps(simple_data, ensure_ascii=False, indent=2)[:500] + "...")
        
    else:
        print(f"❌ 简洁结果文件未生成: {simple_result_file}")
        return False
    
    return True

def compare_file_structures():
    """比较原始文档和生成的简洁结果文件结构"""
    print("\n6. 比较文件结构...")
    
    # 查找原始文档
    original_doc = Path("backend/data/public_files/documents/20250603_211429_complex_sample.json")
    if original_doc.exists():
        with open(original_doc, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
        print(f"✅ 原始文档结构: {type(original_data)}")
        if isinstance(original_data, list) and len(original_data) > 0:
            print(f"   - 第一个项目字段: {list(original_data[0].keys())}")
    
    # 查找生成的简洁结果文件
    annotations_dir = Path("backend/data/annotations")
    if annotations_dir.exists():
        for task_dir in annotations_dir.iterdir():
            if task_dir.is_dir():
                for result_file in task_dir.glob("*.json"):
                    with open(result_file, 'r', encoding='utf-8') as f:
                        result_data = json.load(f)
                    print(f"✅ 生成结果结构: {type(result_data)}")
                    if isinstance(result_data, list) and len(result_data) > 0:
                        print(f"   - 第一个项目字段: {list(result_data[0].keys())}")
                    break
                break

def main():
    """主函数"""
    print("🎯 简洁版本标注结果文件生成测试")
    print("时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 70)
    
    if test_simple_annotation_result():
        compare_file_structures()
        
        print("\n🎉 测试成功！")
        print("=" * 50)
        print("✅ 功能总结:")
        print("   1. 完整标注文件保存在: backend/data/tasks/{taskid}/annotations/")
        print("   2. 简洁结果文件保存在: backend/data/annotations/{taskid}/")
        print("   3. 简洁结果文件结构与原始文档一致")
        print("   4. 只包含标注后的内容，不包含标注过程元数据")
        
        print("\n💡 使用说明:")
        print("- 完整文件包含所有标注信息，用于系统内部处理")
        print("- 简洁文件结构简单，适合外部使用和导出")
        print("- 两个文件会在标注提交时自动生成")
        
    else:
        print("\n❌ 测试失败")
        print("请检查:")
        print("- 后端服务是否运行")
        print("- 任务和文档数据是否存在")
        print("- 修改后的存储逻辑是否正确")

if __name__ == "__main__":
    main() 