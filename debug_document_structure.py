#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试文档数据结构和字段路径问题
"""

import requests
import json

def check_document_content():
    """检查文档内容结构"""
    print("=== 检查文档内容结构 ===")
    
    try:
        # 获取文档内容
        response = requests.get('http://localhost:8000/api/annotations/task_26090d51/documents/doc_f56fcb01/content')
        if response.status_code == 200:
            data = response.json()
            print("API响应结构:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # 分析内容结构
            if 'content' in data and data['content']:
                content = data['content']
                print(f"\n内容类型: {type(content)}")
                
                if isinstance(content, dict):
                    print("内容字段:")
                    for key in content.keys():
                        print(f"  {key}: {type(content[key])}")
                        
                    # 检查items字段
                    if 'items' in content and isinstance(content['items'], list):
                        print(f"\nitems数组长度: {len(content['items'])}")
                        if content['items']:
                            first_item = content['items'][0]
                            print("第一个item的结构:")
                            print(json.dumps(first_item, indent=2, ensure_ascii=False))
                            
        else:
            print(f"请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"错误: {e}")

def check_form_config():
    """检查表单配置"""
    print("\n=== 检查表单配置 ===")
    
    try:
        response = requests.get('http://localhost:8000/api/annotations/task_26090d51/documents/doc_f56fcb01/form-config')
        if response.status_code == 200:
            data = response.json()
            print("表单配置:")
            
            if 'annotation_schema' in data:
                annotation_schema = data['annotation_schema']
                print(f"标注字段数量: {len(annotation_schema)}")
                
                print("\n标注字段路径:")
                for field in annotation_schema:
                    print(f"  {field.get('path', 'N/A')}: {field.get('field_type', 'N/A')}")
                    
        else:
            print(f"请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"错误: {e}")

def test_array_path_parsing():
    """测试数组路径解析"""
    print("\n=== 测试数组路径解析 ===")
    
    # 模拟文档结构
    sample_doc = {
        "items": [
            {
                "document_info": {
                    "title": "Sample Title",
                    "category": "Sample Category",
                    "metadata": {
                        "author": "Sample Author",
                        "publish_date": "2024-01-01"
                    }
                },
                "content_sections": [
                    {
                        "text": "Section 1 text",
                        "annotations": {
                            "sentiment_score": 0.8
                        },
                        "subsections": [
                            {
                                "content": "Subsection content",
                                "analysis": {
                                    "topic": "Sample topic"
                                }
                            }
                        ]
                    }
                ]
            }
        ],
        "type": "array",
        "count": 1
    }
    
    def get_nested_value_with_arrays(obj, path):
        """支持数组路径的取值函数"""
        if not obj or not path:
            return None
            
        # 处理数组路径 content_sections[].text
        if '[].' in path:
            # 先找到数组部分
            parts = path.split('[].')
            array_path = parts[0]  # content_sections
            remaining_path = parts[1]  # text
            
            # 获取数组
            current = obj
            for key in array_path.split('.'):
                if current and isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return None
                    
            # 如果是数组，取第一个元素
            if isinstance(current, list) and current:
                current = current[0]
                
                # 继续解析剩余路径
                for key in remaining_path.split('.'):
                    if current and isinstance(current, dict) and key in current:
                        current = current[key]
                    else:
                        return None
                        
                return current
                
        else:
            # 普通路径处理
            keys = path.split('.')
            current = obj
            for key in keys:
                if current and isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return None
            return current
    
    # 测试路径
    test_paths = [
        "items[0].document_info.title",
        "content_sections[].text", 
        "content_sections[].annotations.sentiment_score",
        "content_sections[].subsections[].content"
    ]
    
    print("原始文档结构:")
    print(json.dumps(sample_doc, indent=2, ensure_ascii=False))
    
    print("\n路径测试结果:")
    for path in test_paths:
        # 先处理特殊的items[0]路径
        if path.startswith("items[0]."):
            actual_path = path.replace("items[0].", "")
            if sample_doc.get("items") and len(sample_doc["items"]) > 0:
                first_item = sample_doc["items"][0]
                value = get_nested_value_with_arrays(first_item, actual_path)
            else:
                value = None
        else:
            value = get_nested_value_with_arrays(sample_doc, path)
            
        print(f"  {path}: {value}")

def main():
    """主函数"""
    print("🔍 调试文档数据结构和字段路径问题...")
    
    # 检查实际的API数据
    check_document_content()
    check_form_config()
    
    # 测试路径解析逻辑
    test_array_path_parsing()

if __name__ == "__main__":
    main() 