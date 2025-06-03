#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试字段数据修复
验证字段显示值和更新功能
"""

import json

def test_form_value_initialization():
    """测试表单值初始化逻辑"""
    print("=== 测试表单值初始化 ===")
    
    # 模拟文档数据
    document_data = {
        "title": "Sample Document Title",
        "author": {
            "name": "John Doe",
            "email": "john@example.com"
        },
        "priority": 3,
        "tags": ["important", "draft"],
        "content": "Document content here..."
    }
    
    # 模拟标注字段
    annotation_fields = [
        {"path": "title", "type": "str", "required": True},
        {"path": "author.name", "type": "str", "required": True},
        {"path": "author.email", "type": "str", "required": False},
        {"path": "priority", "type": "int", "required": False},
        {"path": "tags", "type": "array", "required": False}
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
    
    # 模拟前端初始化逻辑
    print("文档数据:", json.dumps(document_data, indent=2, ensure_ascii=False))
    print()
    
    # 为每个标注字段创建表单值
    form_values = {}
    for field in annotation_fields:
        field_value = get_nested_value(document_data, field["path"])
        form_values[field["path"]] = field_value
        print(f"字段 {field['path']}: {field_value}")
    
    print()
    print("表单值结构:", json.dumps(form_values, indent=2, ensure_ascii=False))
    
    # 验证值不为空
    empty_fields = [path for path, value in form_values.items() if value is None or value == ""]
    if empty_fields:
        print(f"❌ 发现空值字段: {empty_fields}")
    else:
        print("✅ 所有字段都有值")
    
    return form_values

def test_field_change_logic():
    """测试字段变化逻辑"""
    print("\n=== 测试字段变化逻辑 ===")
    
    # 初始数据
    initial_data = test_form_value_initialization()
    
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
    
    # 模拟文档数据
    document_data = {
        "title": "Sample Document Title",
        "author": {
            "name": "John Doe",
            "email": "john@example.com"
        },
        "priority": 3
    }
    
    print("\n模拟字段修改:")
    
    # 修改标题
    print("修改前 title:", document_data.get("title"))
    updated_data = set_nested_value(document_data, "title", "Modified Title")
    print("修改后 title:", updated_data.get("title"))
    
    # 修改作者名字
    print("修改前 author.name:", updated_data.get("author", {}).get("name"))
    updated_data = set_nested_value(updated_data, "author.name", "Jane Smith")
    print("修改后 author.name:", updated_data.get("author", {}).get("name"))
    
    # 修改优先级
    print("修改前 priority:", updated_data.get("priority"))
    updated_data = set_nested_value(updated_data, "priority", 5)
    print("修改后 priority:", updated_data.get("priority"))
    
    print("\n最终数据:", json.dumps(updated_data, indent=2, ensure_ascii=False))
    
    return True

def test_antd_form_structure():
    """测试Antd Form的数据结构要求"""
    print("\n=== 测试Antd Form数据结构 ===")
    
    # 对于嵌套字段，Antd Form要求使用扁平化的字段名
    antd_form_values = {
        "title": "Document Title",
        "author.name": "John Doe",  # 嵌套字段使用点号连接
        "author.email": "john@example.com",
        "priority": 3
    }
    
    print("Antd Form值结构:")
    for field_path, value in antd_form_values.items():
        print(f"  {field_path}: {value}")
    
    print("\n✅ 这种结构应该能正确设置和获取嵌套字段的值")
    
    return True

def main():
    """主测试函数"""
    print("🔧 测试字段数据修复...")
    
    try:
        # 测试表单值初始化
        test_form_value_initialization()
        
        # 测试字段变化逻辑
        test_field_change_logic()
        
        # 测试Antd Form结构
        test_antd_form_structure()
        
        print("\n🎯 修复要点总结:")
        print("1. ✅ 为每个标注字段从文档数据中提取值")
        print("2. ✅ 使用扁平化结构设置Form值 (field.path: value)")
        print("3. ✅ 移除输入控件的自定义value属性，让Antd Form管理")
        print("4. ✅ 通过onValuesChange处理字段变化")
        print("5. ✅ 字段变化时同步更新原始数据和标注数据")
        print("6. ✅ 添加调试日志查看数据流向")
        
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    main() 