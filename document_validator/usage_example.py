#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用示例：演示如何使用增强的文档验证器
"""

import json
from enhanced_validator import EnhancedDocumentValidator

def main():
    print("=== 文档验证器使用示例 ===\n")
    
    # 1. 初始化验证器
    print("1. 初始化验证器...")
    validator = EnhancedDocumentValidator("complex_template.py")
    print(f"   主模型: {validator.model.__name__}")
    print(f"   标注字段数量: {len(validator.annotation_fields)}\n")
    
    # 2. 显示标注字段模式
    print("2. 标注字段模式:")
    schema = validator.get_annotation_schema()
    for field in schema[:5]:  # 只显示前5个字段
        print(f"   路径: {field['path']}")
        print(f"   类型: {field['type']} | 必需: {field['required']}")
        print(f"   描述: {field['description']}")
        if field['constraints']:
            print(f"   约束: {field['constraints']}")
        print()
    
    if len(schema) > 5:
        print(f"   ... 还有 {len(schema) - 5} 个字段\n")
    
    # 3. 验证示例文档
    print("3. 验证示例文档...")
    sample_doc = {
        "id": "example_001",
        "text1": "这是一个示例文档，展示了复杂的嵌套结构标注功能。",
        "end": 800,
        "document_info": {
            "title": "示例文档标题",
            "category": "示例类别",
            "metadata": {
                "author": "示例作者",
                "publish_date": "2024-01-20",
                "classification": "公开"
            }
        },
        "content_sections": [
            {
                "section_id": "section1",
                "text": "第一个章节的内容",
                "annotations": {
                    "sentiment_score": 0.6,
                    "key_entities": ["示例", "章节"],
                    "importance_level": 3
                },
                "subsections": [
                    {
                        "subsection_id": "sub1",
                        "content": "子章节内容",
                        "analysis": {
                            "topic": "示例主题",
                            "confidence": 0.9
                        }
                    }
                ]
            }
        ],
        "statistics": {
            "word_count": 500,
            "paragraph_count": 3,
            "reading_time": 2
        }
    }
    
    # 验证文档
    validation_result = validator.validate_document(sample_doc)
    if validation_result["valid"]:
        print("   ✓ 文档验证通过")
    else:
        print("   ✗ 文档验证失败:")
        for error in validation_result["errors"]:
            print(f"     - {error}")
    
    # 4. 提取标注字段
    print("\n4. 提取标注字段值:")
    annotations = validator.extract_annotations(sample_doc)
    
    for path, value in annotations.items():
        if isinstance(value, list) and len(value) > 0:
            if isinstance(value[0], list):
                # 嵌套列表
                print(f"   {path}: {value}")
            else:
                # 简单列表
                print(f"   {path}: {value}")
        else:
            print(f"   {path}: {value}")
    
    print(f"\n   总共提取了 {len(annotations)} 个标注字段值")
    
    # 5. 验证复杂示例文件
    print("\n5. 验证复杂示例文件...")
    file_result = validator.validate_file("complex_sample.json")
    print(f"   文件验证结果:")
    print(f"   - 总文档数: {file_result['total']}")
    print(f"   - 有效文档: {file_result['valid_count']}")
    print(f"   - 无效文档: {file_result['invalid_count']}")
    
    # 6. 保存结果
    print("\n6. 保存结果到文件...")
    result = {
        "document": sample_doc,
        "validation": validation_result,
        "annotations": annotations,
        "schema": schema,
        "file_validation": file_result
    }
    
    with open("validation_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    
    print("   结果已保存到 validation_result.json")
    
    # 7. 演示错误处理
    print("\n7. 演示错误处理...")
    invalid_doc = {
        "id": "invalid_example",
        "text1": "",  # 空字符串
        "end": -1,  # 负数，违反ge=0约束
        "document_info": {
            "title": "短",  # 太短，违反min_length=5约束
            "category": "类别",
            "metadata": {
                "author": "作者",
                "publish_date": "2024-01-20",
                "classification": "公开"
            }
        },
        "content_sections": [
            {
                "section_id": "section1",
                "text": "内容",
                "annotations": {
                    "sentiment_score": 2.0,  # 超出范围，违反le=1.0约束
                    "key_entities": ["实体"],
                    "importance_level": 10  # 超出范围，违反le=5约束
                }
            }
        ],
        "statistics": {
            "word_count": 100,
            "paragraph_count": 1,
            "reading_time": 1
        }
    }
    
    invalid_result = validator.validate_document(invalid_doc)
    if not invalid_result["valid"]:
        print("   ✓ 成功检测到无效文档")
        print("   错误详情:")
        for error in invalid_result["errors"][:3]:  # 只显示前3个错误
            print(f"     - {error['loc']}: {error['msg']}")
        if len(invalid_result["errors"]) > 3:
            print(f"     ... 还有 {len(invalid_result['errors']) - 3} 个错误")
    
    print("\n=== 演示完成 ===")

if __name__ == "__main__":
    main() 