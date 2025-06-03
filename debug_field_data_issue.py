#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试字段数据问题的脚本
检查字段为空和更新不生效的问题
"""

import json
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def debug_nested_value_functions():
    """调试嵌套值获取和设置函数"""
    print("=== 调试嵌套值函数 ===")
    
    # 模拟JavaScript的getNestedValue函数
    def get_nested_value(obj, path):
        """模拟前端的getNestedValue函数"""
        if not obj or not path:
            return None
        
        keys = path.split('.')
        current = obj
        for key in keys:
            if current and isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current
    
    # 模拟JavaScript的setNestedValue函数
    def set_nested_value(obj, path, value):
        """模拟前端的setNestedValue函数"""
        if not path:
            return obj
        
        import copy
        result = copy.deepcopy(obj)
        keys = path.split('.')
        current = result
        
        for i in range(len(keys) - 1):
            key = keys[i]
            if key not in current or not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
        return result
    
    # 测试数据
    test_document = {
        "title": "Sample Document",
        "author": {
            "name": "John Doe",
            "email": "john@example.com"
        },
        "priority": 3,
        "tags": ["important", "draft"],
        "metadata": {
            "created_at": "2024-01-01",
            "status": "active"
        }
    }
    
    # 测试字段路径
    test_paths = [
        "title",
        "author.name", 
        "author.email",
        "priority",
        "metadata.status",
        "nonexistent.field"
    ]
    
    print("原始文档数据:")
    print(json.dumps(test_document, indent=2, ensure_ascii=False))
    print()
    
    print("测试获取嵌套值:")
    for path in test_paths:
        value = get_nested_value(test_document, path)
        print(f"  {path}: {value}")
    print()
    
    # 测试设置嵌套值
    print("测试设置嵌套值:")
    updated_doc = test_document.copy()
    
    # 修改标题
    updated_doc = set_nested_value(updated_doc, "title", "Modified Title")
    print(f"修改 title: {get_nested_value(updated_doc, 'title')}")
    
    # 修改作者名字
    updated_doc = set_nested_value(updated_doc, "author.name", "Jane Smith")
    print(f"修改 author.name: {get_nested_value(updated_doc, 'author.name')}")
    
    # 修改优先级
    updated_doc = set_nested_value(updated_doc, "priority", 5)
    print(f"修改 priority: {get_nested_value(updated_doc, 'priority')}")
    
    print("\n修改后的文档:")
    print(json.dumps(updated_doc, indent=2, ensure_ascii=False))
    
    return True

def debug_data_initialization():
    """调试数据初始化逻辑"""
    print("\n=== 调试数据初始化逻辑 ===")
    
    # 模拟当前文档数据
    current_document = {
        "id": "doc_123",
        "filename": "test.json",
        "originalContent": {
            "title": "Original Title",
            "author": {
                "name": "Original Author",
                "email": "original@example.com"
            },
            "priority": 2,
            "content": "Original content..."
        },
        "annotatedContent": {
            "title": "Annotated Title",
            "author": {
                "name": "Annotated Author"
            },
            "priority": 4
        }
    }
    
    # 模拟标注字段配置
    annotation_fields = [
        {
            "path": "title",
            "type": "str",
            "required": True,
            "description": "Document Title"
        },
        {
            "path": "author.name", 
            "type": "str",
            "required": True,
            "description": "Author Name"
        },
        {
            "path": "priority",
            "type": "int", 
            "required": False,
            "description": "Priority Level"
        }
    ]
    
    def get_nested_value(obj, path):
        if not obj or not path:
            return None
        keys = path.split('.')
        current = obj
        for key in keys:
            if current and isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current
    
    def set_nested_value(obj, path, value):
        if not path:
            return obj
        import copy
        result = copy.deepcopy(obj)
        keys = path.split('.')
        current = result
        for i in range(len(keys) - 1):
            key = keys[i]
            if key not in current or not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
        return result
    
    print("当前文档数据:")
    print("originalContent:", json.dumps(current_document["originalContent"], indent=2, ensure_ascii=False))
    print("annotatedContent:", json.dumps(current_document["annotatedContent"], indent=2, ensure_ascii=False))
    print()
    
    # 模拟前端初始化逻辑
    original_data = current_document["originalContent"] or {}
    
    # 为标注字段设置原始值
    fields_with_original_values = []
    for field in annotation_fields:
        field_copy = field.copy()
        field_copy["originalValue"] = get_nested_value(original_data, field["path"])
        fields_with_original_values.append(field_copy)
    
    print("字段原始值:")
    for field in fields_with_original_values:
        print(f"  {field['path']}: {field['originalValue']}")
    print()
    
    # 使用原文档内容作为标注数据的初始值
    initial_annotation_data = original_data.copy()
    
    # 检查已有的标注数据，如果存在则覆盖对应字段
    existing_annotation_data = current_document["annotatedContent"] or {}
    for field in fields_with_original_values:
        existing_value = get_nested_value(existing_annotation_data, field["path"])
        if existing_value is not None:
            initial_annotation_data = set_nested_value(initial_annotation_data, field["path"], existing_value)
    
    print("初始化后的标注数据:")
    print(json.dumps(initial_annotation_data, indent=2, ensure_ascii=False))
    print()
    
    # 验证字段值
    print("字段值验证:")
    for field in fields_with_original_values:
        current_value = get_nested_value(initial_annotation_data, field["path"])
        original_value = field["originalValue"]
        print(f"  {field['path']}:")
        print(f"    当前值: {current_value}")
        print(f"    原始值: {original_value}")
        print(f"    是否为空: {current_value is None or current_value == ''}")
    
    return initial_annotation_data, fields_with_original_values

def debug_field_change_logic():
    """调试字段变化逻辑"""
    print("\n=== 调试字段变化逻辑 ===")
    
    # 使用之前初始化的数据
    initial_data, fields = debug_data_initialization()
    
    def get_nested_value(obj, path):
        if not obj or not path:
            return None
        keys = path.split('.')
        current = obj
        for key in keys:
            if current and isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current
    
    def set_nested_value(obj, path, value):
        if not path:
            return obj
        import copy
        result = copy.deepcopy(obj)
        keys = path.split('.')
        current = result
        for i in range(len(keys) - 1):
            key = keys[i]
            if key not in current or not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
        return result
    
    # 模拟本地缓冲区
    local_buffer = {
        "originalData": initial_data.copy(),
        "annotationData": initial_data.copy(),
        "modifiedFields": set()
    }
    
    print("模拟字段修改:")
    
    # 修改标题
    field_path = "title"
    new_value = "New Modified Title"
    
    print(f"\n修改字段: {field_path} -> {new_value}")
    print(f"修改前:")
    print(f"  originalData[{field_path}]: {get_nested_value(local_buffer['originalData'], field_path)}")
    print(f"  annotationData[{field_path}]: {get_nested_value(local_buffer['annotationData'], field_path)}")
    
    # 执行修改逻辑
    updated_annotation_data = set_nested_value(local_buffer["annotationData"], field_path, new_value)
    updated_original_data = set_nested_value(local_buffer["originalData"], field_path, new_value)
    
    local_buffer["annotationData"] = updated_annotation_data
    local_buffer["originalData"] = updated_original_data
    local_buffer["modifiedFields"].add(field_path)
    
    print(f"修改后:")
    print(f"  originalData[{field_path}]: {get_nested_value(local_buffer['originalData'], field_path)}")
    print(f"  annotationData[{field_path}]: {get_nested_value(local_buffer['annotationData'], field_path)}")
    
    # 修改嵌套字段
    field_path = "author.name"
    new_value = "New Author Name"
    
    print(f"\n修改嵌套字段: {field_path} -> {new_value}")
    print(f"修改前:")
    print(f"  originalData[{field_path}]: {get_nested_value(local_buffer['originalData'], field_path)}")
    print(f"  annotationData[{field_path}]: {get_nested_value(local_buffer['annotationData'], field_path)}")
    
    # 执行修改逻辑
    updated_annotation_data = set_nested_value(local_buffer["annotationData"], field_path, new_value)
    updated_original_data = set_nested_value(local_buffer["originalData"], field_path, new_value)
    
    local_buffer["annotationData"] = updated_annotation_data
    local_buffer["originalData"] = updated_original_data
    local_buffer["modifiedFields"].add(field_path)
    
    print(f"修改后:")
    print(f"  originalData[{field_path}]: {get_nested_value(local_buffer['originalData'], field_path)}")
    print(f"  annotationData[{field_path}]: {get_nested_value(local_buffer['annotationData'], field_path)}")
    
    print(f"\n最终数据状态:")
    print("originalData:", json.dumps(local_buffer["originalData"], indent=2, ensure_ascii=False))
    print("annotationData:", json.dumps(local_buffer["annotationData"], indent=2, ensure_ascii=False))
    print("modifiedFields:", list(local_buffer["modifiedFields"]))
    
    return True

def main():
    """主调试函数"""
    print("🔍 开始调试字段数据问题...")
    
    try:
        # 测试基础函数
        debug_nested_value_functions()
        
        # 测试数据初始化
        debug_data_initialization() 
        
        # 测试字段变化逻辑
        debug_field_change_logic()
        
        print("\n🎯 调试完成 - 检查以上输出以诊断问题")
        print("\n可能的问题原因:")
        print("1. 字段值为空 - 检查 originalContent 是否包含标注字段的数据")
        print("2. 修改不生效 - 检查 handleFieldChange 函数是否正确调用")
        print("3. 表单初始化 - 检查 form.setFieldsValue 是否使用正确的数据结构")
        print("4. 路径匹配 - 检查标注字段路径是否与文档数据结构匹配")
        
    except Exception as e:
        print(f"调试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 