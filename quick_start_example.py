#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速开始示例
演示如何在实际项目中使用简化版文档校验模块
"""

from simple_document_validator import SimpleDocumentValidator
import json

def main():
    print("🚀 简化版文档校验模块 - 快速开始示例")
    print("=" * 50)
    
    # 步骤1：创建验证器并加载模板
    print("\n📋 步骤1：加载文档模板")
    validator = SimpleDocumentValidator("simple_template_example.py")
    
    if not validator.main_model:
        print("❌ 模板加载失败")
        return
    
    print(f"✅ 模板加载成功: {validator.main_model.__name__}")
    
    # 步骤2：准备要验证的文档数据
    print("\n📄 步骤2：准备文档数据")
    document_data = {
        "id": "example_doc_001",
        "title": "人工智能在医疗领域的应用研究",
        "document_type": "研究",
        "summary": "本文探讨了人工智能技术在医疗诊断、药物研发等领域的最新应用进展。",
        "author": {
            "name": "王医生",
            "affiliation": "北京大学医学院",
            "email": "wang.doctor@pku.edu.cn"
        },
        "paragraphs": [
            {
                "content": "人工智能技术正在革命性地改变医疗行业的诊断和治疗方式。",
                "page_number": 1,
                "sentiment_score": 0.8,
                "keywords": ["人工智能", "医疗", "诊断"]
            },
            {
                "content": "深度学习算法在医学影像分析中展现出了超越人类专家的准确性。",
                "page_number": 2,
                "sentiment_score": 0.9,
                "keywords": ["深度学习", "医学影像", "准确性"]
            }
        ],
        "tags": ["人工智能", "医疗", "研究"],
        "created_at": "2024-01-20T15:30:00Z",
        "word_count": 2500
    }
    
    print("📝 文档数据准备完成")
    
    # 步骤3：验证文档
    print("\n🔍 步骤3：验证文档结构")
    validation_result = validator.validate_document(document_data)
    
    if validation_result["valid"]:
        print("✅ 文档验证通过")
    else:
        print("❌ 文档验证失败:")
        for error in validation_result["errors"][:3]:  # 只显示前3个错误
            print(f"   - {error['loc']}: {error['msg']}")
        return
    
    # 步骤4：提取标注字段
    print("\n📊 步骤4：提取标注字段")
    annotations = validator.extract_annotations(document_data)
    
    print("提取到的标注字段:")
    for path, value in annotations.items():
        if isinstance(value, list):
            if len(value) <= 3:  # 短列表直接显示
                print(f"   {path}: {value}")
            else:  # 长列表显示前几个
                print(f"   {path}: {value[:2]}... (共{len(value)}项)")
        elif isinstance(value, str) and len(value) > 50:
            print(f"   {path}: {value[:47]}...")
        else:
            print(f"   {path}: {value}")
    
    print(f"\n📈 总共提取了 {len(annotations)} 个标注字段")
    
    # 步骤5：获取字段模式信息
    print("\n📋 步骤5：查看字段模式")
    schema = validator.get_annotation_schema()
    
    print("标注字段模式概览:")
    required_fields = [f for f in schema if f['required']]
    optional_fields = [f for f in schema if not f['required']]
    
    print(f"   必填字段: {len(required_fields)} 个")
    print(f"   可选字段: {len(optional_fields)} 个")
    
    # 显示几个重要字段的详细信息
    important_fields = ["title", "author.name", "paragraphs[].content"]
    print("\n重要字段详情:")
    for field in schema:
        if field['path'] in important_fields:
            print(f"   📌 {field['path']}")
            print(f"      类型: {field['type']}")
            print(f"      必需: {'是' if field['required'] else '否'}")
            print(f"      描述: {field['description']}")
            if field['constraints']:
                print(f"      约束: {field['constraints']}")
            print()
    
    # 步骤6：实际应用场景演示
    print("🎯 步骤6：实际应用场景演示")
    
    # 场景1：批量验证多个文档
    print("\n场景1：批量验证文档")
    documents = [document_data]  # 在实际应用中，这里会是多个文档
    
    valid_count = 0
    for i, doc in enumerate(documents, 1):
        result = validator.validate_document(doc)
        if result["valid"]:
            valid_count += 1
            print(f"   文档 {i}: ✅ 通过")
        else:
            print(f"   文档 {i}: ❌ 失败")
    
    print(f"   批量验证结果: {valid_count}/{len(documents)} 通过")
    
    # 场景2：数据质量检查
    print("\n场景2：数据质量检查")
    quality_issues = []
    
    # 检查标题长度
    title = annotations.get("title", "")
    if len(title) < 10:
        quality_issues.append("标题过短，建议增加描述性内容")
    
    # 检查段落数量
    paragraphs = annotations.get("paragraphs[].content", [])
    if len(paragraphs) < 2:
        quality_issues.append("段落数量较少，建议增加内容")
    
    # 检查关键词
    all_keywords = annotations.get("paragraphs[].keywords", [])
    total_keywords = sum(len(kw_list) for kw_list in all_keywords)
    if total_keywords < 5:
        quality_issues.append("关键词数量较少，建议增加更多关键词")
    
    if quality_issues:
        print("   发现的质量问题:")
        for issue in quality_issues:
            print(f"   ⚠️  {issue}")
    else:
        print("   ✅ 数据质量良好")
    
    # 场景3：生成数据报告
    print("\n场景3：生成数据报告")
    report = {
        "document_id": document_data["id"],
        "validation_status": "通过" if validation_result["valid"] else "失败",
        "annotation_count": len(annotations),
        "quality_score": max(0, 100 - len(quality_issues) * 20),  # 简单的质量评分
        "extracted_data": {
            "title": annotations.get("title"),
            "author": annotations.get("author.name"),
            "paragraph_count": len(annotations.get("paragraphs[].content", [])),
            "keyword_count": sum(len(kw) for kw in annotations.get("paragraphs[].keywords", []))
        }
    }
    
    print("   📊 数据报告:")
    for key, value in report.items():
        if key == "extracted_data":
            print(f"   {key}:")
            for sub_key, sub_value in value.items():
                print(f"      {sub_key}: {sub_value}")
        else:
            print(f"   {key}: {value}")
    
    print("\n🎉 演示完成！")
    print("\n💡 使用提示:")
    print("   1. 在实际项目中，可以将验证器集成到数据处理流水线中")
    print("   2. 可以根据验证结果自动分类和处理文档")
    print("   3. 提取的标注字段可以直接用于机器学习训练")
    print("   4. 字段模式信息可以用于生成前端表单")

if __name__ == "__main__":
    main() 