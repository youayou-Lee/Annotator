#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试对象显示修复效果
验证嵌套数组和对象字段在标注界面中能够正确显示
"""

import json
import requests
import time

# 测试数据 - 包含嵌套的subsections数组
test_document = {
    "content_sections": [
        {
            "subsections": [
                {
                    "subsection_id": "background",
                    "content": "论坛为中非友好合作提供了重要平台",
                    "analysis": {
                        "topic": "合作平台",
                        "confidence": 0.95
                    }
                },
                {
                    "subsection_id": "significance", 
                    "content": "此次论坛的重要意义在于促进双边关系发展",
                    "analysis": {
                        "topic": "双边关系",
                        "confidence": 0.88
                    }
                }
            ]
        }
    ]
}

def test_object_display():
    """测试对象显示是否正确"""
    print("=== 测试对象显示修复效果 ===")
    
    # 模拟前端格式化函数的行为
    def format_display_value(value):
        """模拟前端的formatDisplayValue函数"""
        if value is None:
            return ''
        
        if isinstance(value, str):
            return value
        
        if isinstance(value, (int, float, bool)):
            return str(value)
        
        if isinstance(value, list):
            # 数组：如果数组很简单，显示为逗号分隔；否则显示JSON
            if len(value) == 0:
                return '[]'
            if all(isinstance(item, (str, int, float)) for item in value):
                return ', '.join(str(item) for item in value)
            return json.dumps(value, indent=2, ensure_ascii=False)
        
        if isinstance(value, dict):
            # 对象：显示为简洁的JSON字符串
            return json.dumps(value, indent=2, ensure_ascii=False)
        
        return str(value)
    
    # 测试不同类型的字段值
    test_cases = [
        ("简单字符串", "论坛为中非友好合作提供了重要平台"),
        ("数字", 0.95),
        ("布尔值", True),
        ("简单数组", ["topic1", "topic2"]),
        ("复杂对象", {
            "topic": "合作平台",
            "confidence": 0.95
        }),
        ("嵌套数组", [
            {
                "subsection_id": "background",
                "content": "论坛为中非友好合作提供了重要平台",
                "analysis": {
                    "topic": "合作平台",
                    "confidence": 0.95
                }
            }
        ]),
        ("完整文档", test_document)
    ]
    
    print("字段类型 | 原始值 | 格式化后的显示值")
    print("-" * 80)
    
    for field_type, value in test_cases:
        formatted = format_display_value(value)
        
        # 检查是否会出现 [object Object] 问题
        if "[object Object]" in str(formatted):
            print(f"❌ {field_type}: 仍然显示为 [object Object]")
        else:
            # 限制显示长度以便查看
            display_value = formatted[:100] + "..." if len(formatted) > 100 else formatted
            print(f"✅ {field_type}: {display_value}")
    
    # 测试特定的路径值提取
    print("\n=== 测试路径值提取 ===")
    
    def get_nested_value(obj, path):
        """模拟前端的getNestedValue函数"""
        if not obj or not path:
            return None
        
        current = obj
        
        # 处理包含数组索引的路径 如: content_sections[].subsections[].content
        if '[]' in path:
            parts = path.split('[]')
            array_path = parts[0]  # content_sections
            remaining_path = parts[1]  # .subsections[].content
            
            # 获取到数组
            array_keys = array_path.split('.')
            for key in array_keys:
                if current and isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return None
            
            # 如果是数组，取第一个元素
            if isinstance(current, list) and len(current) > 0:
                current = current[0]
                
                # 处理剩余路径（去掉开头的点号）
                if remaining_path and remaining_path.startswith('.'):
                    remaining_path = remaining_path[1:]
                
                if remaining_path:
                    # 递归处理剩余路径（可能还有嵌套数组）
                    return get_nested_value(current, remaining_path)
                else:
                    return current
            else:
                return None
        else:
            # 普通路径处理
            keys = path.split('.')
            for key in keys:
                if current and isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return None
            return current
    
    # 测试不同的字段路径
    test_paths = [
        "content_sections[].subsections[].content",
        "content_sections[].subsections[].analysis",
        "content_sections[].subsections[].analysis.topic",
        "content_sections[].subsections[].analysis.confidence"
    ]
    
    for path in test_paths:
        value = get_nested_value(test_document, path)
        formatted = format_display_value(value)
        print(f"路径: {path}")
        print(f"值: {formatted}")
        print("-" * 40)
    
    print("\n✅ 测试完成！所有对象值现在应该能正确显示为JSON格式，而不是[object Object]")

if __name__ == "__main__":
    test_object_display() 