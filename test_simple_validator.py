#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版文档校验模块测试脚本
演示所有核心功能的使用方法
"""

import json
from simple_document_validator import SimpleDocumentValidator

def print_separator(title):
    """打印分隔线"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_subsection(title):
    """打印子标题"""
    print(f"\n{'-'*40}")
    print(f" {title}")
    print(f"{'-'*40}")

def main():
    print_separator("简化版文档校验模块测试")
    
    # 1. 创建验证器并加载模板
    print_subsection("1. 加载模板文件")
    validator = SimpleDocumentValidator()
    
    # 加载模板
    template_result = validator.load_template("simple_template_example.py")
    print(f"模板加载结果: {template_result}")
    
    if not template_result["valid"]:
        print("❌ 模板加载失败，无法继续测试")
        return
    
    print(f"✅ 模板加载成功")
    print(f"   主模型: {template_result['main_model']}")
    print(f"   标注字段数量: {template_result['annotation_fields_count']}")
    
    # 2. 显示标注字段模式
    print_subsection("2. 标注字段模式信息")
    schema = validator.get_annotation_schema()
    
    print(f"共发现 {len(schema)} 个标注字段:")
    for i, field in enumerate(schema, 1):
        print(f"\n  {i}. 路径: {field['path']}")
        print(f"     类型: {field['type']}")
        print(f"     必需: {'是' if field['required'] else '否'}")
        print(f"     描述: {field['description']}")
        if field['constraints']:
            print(f"     约束: {field['constraints']}")
    
    # 3. 验证单个文档
    print_subsection("3. 单个文档验证")
    
    # 有效文档
    valid_doc = {
        "id": "test_001",
        "title": "测试文档标题",
        "document_type": "新闻",
        "summary": "这是一个测试文档的摘要信息。",
        "author": {
            "name": "测试作者",
            "affiliation": "测试机构",
            "email": "test@example.com"
        },
        "paragraphs": [
            {
                "content": "这是第一个段落的内容，包含了足够的文字来满足最小长度要求。",
                "page_number": 1,
                "sentiment_score": 0.5,
                "keywords": ["测试", "段落"]
            }
        ],
        "tags": ["测试", "示例"],
        "created_at": "2024-01-20T10:00:00Z",
        "word_count": 100
    }
    
    print("验证有效文档:")
    valid_result = validator.validate_document(valid_doc)
    print(f"  结果: {'✅ 通过' if valid_result['valid'] else '❌ 失败'}")
    if not valid_result["valid"]:
        print(f"  错误: {valid_result.get('errors', valid_result.get('error'))}")
    
    # 无效文档
    print("\n验证无效文档:")
    invalid_doc = {
        "id": "test_002",
        "title": "短",  # 太短，违反min_length=5
        "document_type": "无效类型",  # 不在枚举中
        "author": {
            "name": "A",  # 太短，违反min_length=2
            "affiliation": "测试机构"
        },
        "paragraphs": [
            {
                "content": "太短",  # 违反min_length=10
                "page_number": 0,  # 违反ge=1
                "sentiment_score": 2.0  # 违反le=1.0
            }
        ]
    }
    
    invalid_result = validator.validate_document(invalid_doc)
    print(f"  结果: {'✅ 通过' if invalid_result['valid'] else '❌ 失败'}")
    if not invalid_result["valid"]:
        print("  错误详情:")
        errors = invalid_result.get('errors', [])
        for i, error in enumerate(errors[:5], 1):  # 只显示前5个错误
            print(f"    {i}. {error['loc']}: {error['msg']}")
        if len(errors) > 5:
            print(f"    ... 还有 {len(errors) - 5} 个错误")
    
    # 4. 提取标注字段
    print_subsection("4. 标注字段提取")
    annotations = validator.extract_annotations(valid_doc)
    
    print("从有效文档中提取的标注字段:")
    for path, value in annotations.items():
        if isinstance(value, list) and len(value) > 0:
            if isinstance(value[0], list):
                # 嵌套列表
                print(f"  {path}: {value}")
            else:
                # 简单列表
                print(f"  {path}: {value}")
        else:
            print(f"  {path}: {value}")
    
    print(f"\n总共提取了 {len(annotations)} 个标注字段值")
    
    # 5. 文件验证
    print_subsection("5. JSON文件验证")
    
    # 验证测试数据文件
    file_result = validator.validate_file("test_sample_data.json")
    print(f"文件验证结果:")
    print(f"  总文档数: {file_result.get('total', 0)}")
    print(f"  有效文档: {file_result.get('valid_count', 0)}")
    print(f"  无效文档: {file_result.get('invalid_count', 0)}")
    
    if file_result.get("results"):
        print("\n各文档验证详情:")
        for i, result in enumerate(file_result["results"], 1):
            status = "✅ 通过" if result.get("valid") else "❌ 失败"
            print(f"  文档 {i}: {status}")
            if not result.get("valid"):
                error_info = result.get('errors', result.get('error', '未知错误'))
                if isinstance(error_info, list) and len(error_info) > 0:
                    print(f"    错误: {error_info[0]['msg']}")
                else:
                    print(f"    错误: {error_info}")
    
    # 6. 创建验证报告
    print_subsection("6. 生成验证报告")
    
    report = {
        "template_info": {
            "file": "simple_template_example.py",
            "main_model": template_result.get("main_model"),
            "annotation_fields_count": len(schema)
        },
        "schema": schema,
        "test_results": {
            "single_document": {
                "valid_doc": valid_result,
                "invalid_doc": invalid_result
            },
            "file_validation": file_result,
            "extracted_annotations": annotations
        }
    }
    
    # 保存报告
    with open("validation_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    
    print("✅ 验证报告已保存到 validation_report.json")
    
    # 7. 性能测试
    print_subsection("7. 简单性能测试")
    
    import time
    
    # 测试多次验证的性能
    start_time = time.time()
    test_count = 100
    
    for _ in range(test_count):
        validator.validate_document(valid_doc)
    
    end_time = time.time()
    avg_time = (end_time - start_time) / test_count * 1000  # 转换为毫秒
    
    print(f"验证 {test_count} 个文档耗时: {end_time - start_time:.3f} 秒")
    print(f"平均每个文档验证时间: {avg_time:.2f} 毫秒")
    
    print_separator("测试完成")
    print("🎉 所有功能测试完成！")
    print("\n生成的文件:")
    print("  - validation_report.json: 详细验证报告")
    print("\n核心功能:")
    print("  ✅ 模板语法检查")
    print("  ✅ 主模型自动识别")
    print("  ✅ 标注字段递归提取")
    print("  ✅ 文档结构验证")
    print("  ✅ 约束条件检查")
    print("  ✅ 标注字段值提取")
    print("  ✅ JSON/JSONL文件批量验证")

if __name__ == "__main__":
    main() 