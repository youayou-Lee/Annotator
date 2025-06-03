#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试嵌套数组路径修复效果
验证 content_sections[].subsections[].analysis.topic 这样的多层嵌套路径能够正确解析
"""

import json

# 测试数据 - 模拟真实的文档结构
test_document = {
    "items": [
        {
            "id": "xsFX1M41W7MugfX0",
            "text1": "继续发出中非联合自强、团结协作的时代强音，推动以高质量中非合作引领全球南方合作。",
            "end": 1213,
            "document_info": {"title": "测试文档"},
            "content_sections": [
                {
                    "section_id": "intro",
                    "text": "中非合作论坛成立以来，中非关系实现了历史性跨越。",
                    "annotations": {},
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
                },
                {
                    "section_id": "main",
                    "text": "论坛主要内容和议题",
                    "annotations": {},
                    "subsections": [
                        {
                            "subsection_id": "topics",
                            "content": "会议讨论了多个重要议题",
                            "analysis": {
                                "topic": "会议议题",
                                "confidence": 0.92
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

def simulate_get_nested_value(obj, path):
    """
    模拟修复后的前端 getNestedValue 函数
    """
    if not obj or not path:
        return None
    
    print(f"getNestedValue: path={path}")
    
    # 特殊处理：如果文档结构是 {items: [...], type: 'array'}，则从items[0]开始
    current = obj
    if (obj.get('items') and isinstance(obj['items'], list) and 
        len(obj['items']) > 0 and obj.get('type') == 'array'):
        current = obj['items'][0]
        print(f"  使用items[0]作为根对象")
    
    # 处理包含数组索引的路径
    if '[]' in path:
        # 找到第一个数组标记
        first_array_index = path.find('[]')
        before_array = path[:first_array_index]  # content_sections
        after_array = path[first_array_index + 2:]  # .subsections[].analysis.topic
        
        print(f"  数组路径: {before_array}, 剩余路径: {after_array}")
        
        # 获取到数组
        array_keys = before_array.split('.')
        for key in array_keys:
            if current and isinstance(current, dict) and key in current:
                current = current[key]
            else:
                print(f"  数组路径中断在: {key}")
                return None
        
        # 如果是数组，取第一个元素
        if isinstance(current, list) and len(current) > 0:
            current = current[0]
            print(f"  使用数组第一个元素")
            
            # 处理剩余路径（去掉开头的点号）
            remaining_path = after_array
            if remaining_path and remaining_path.startswith('.'):
                remaining_path = remaining_path[1:]
            
            if remaining_path:
                # 递归处理剩余路径（可能还有嵌套数组）
                return simulate_get_nested_value(current, remaining_path)
            else:
                return current
        else:
            print(f"  不是数组或数组为空")
            return None
    else:
        # 普通路径处理
        keys = path.split('.')
        for key in keys:
            if current and isinstance(current, dict) and key in current:
                current = current[key]
            else:
                print(f"  普通路径中断在: {key}")
                return None
        print(f"  普通路径结果: {current}")
        return current

def test_nested_array_paths():
    """测试嵌套数组路径解析"""
    print("=== 测试嵌套数组路径修复效果 ===\n")
    
    # 测试不同的嵌套路径
    test_paths = [
        "content_sections[].subsections[].content",
        "content_sections[].subsections[].analysis",
        "content_sections[].subsections[].analysis.topic", 
        "content_sections[].subsections[].analysis.confidence",
        "content_sections[].section_id",
        "content_sections[].text",
        "content_sections[].subsections[]"
    ]
    
    for path in test_paths:
        print(f"测试路径: {path}")
        print("-" * 50)
        
        result = simulate_get_nested_value(test_document, path)
        
        if result is not None:
            if isinstance(result, (dict, list)):
                formatted_result = json.dumps(result, indent=2, ensure_ascii=False)
                print(f"✅ 成功获取值:\n{formatted_result}")
            else:
                print(f"✅ 成功获取值: {result}")
        else:
            print("❌ 获取值失败: None")
        
        print("\n" + "="*60 + "\n")
    
    # 验证具体值是否正确
    print("=== 验证具体值 ===")
    
    expected_results = [
        ("content_sections[].subsections[].analysis.topic", "合作平台"),
        ("content_sections[].subsections[].analysis.confidence", 0.95),
        ("content_sections[].section_id", "intro"),
        ("content_sections[].subsections[].content", "论坛为中非友好合作提供了重要平台")
    ]
    
    for path, expected in expected_results:
        result = simulate_get_nested_value(test_document, path)
        if result == expected:
            print(f"✅ {path}: {result} (正确)")
        else:
            print(f"❌ {path}: 期望 {expected}, 实际 {result}")
    
    print("\n✅ 嵌套数组路径修复测试完成！")

if __name__ == "__main__":
    test_nested_array_paths() 