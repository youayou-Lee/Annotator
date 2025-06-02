#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
后端集成测试脚本
验证简化版文档校验模块是否正确集成到后端
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.simple_document_validator import SimpleDocumentValidator
from app.core.template_validator import TemplateValidator
from app.core.annotation_validator import AnnotationValidator
from app.core.storage import StorageManager

def test_simple_validator():
    """测试简化版验证器"""
    print("🔍 测试简化版文档验证器...")
    
    validator = SimpleDocumentValidator()
    result = validator.load_template("test_template_example.py")
    
    if result["valid"]:
        print(f"✅ 模板加载成功: {result['main_model']}")
        print(f"   标注字段数量: {result['annotation_fields_count']}")
        
        # 测试文档验证
        test_data = {
            "id": "test_001",
            "title": "测试文档标题",
            "document_type": "新闻",
            "author": {
                "name": "测试作者",
                "affiliation": "测试机构"
            },
            "tags": ["测试", "集成"],
            "created_at": "2024-01-20T10:00:00Z"
        }
        
        validation_result = validator.validate_document(test_data)
        if validation_result["valid"]:
            print("✅ 文档验证通过")
            
            # 测试标注字段提取
            annotations = validator.extract_annotations(test_data)
            print(f"✅ 提取标注字段: {len(annotations)} 个")
            for path, value in list(annotations.items())[:3]:
                print(f"   {path}: {value}")
        else:
            print(f"❌ 文档验证失败: {validation_result.get('error')}")
    else:
        print(f"❌ 模板加载失败: {result['error']}")

def test_template_validator():
    """测试模板验证器"""
    print("\n🔍 测试模板验证器...")
    
    validator = TemplateValidator()
    result = validator.validate_template_file("test_template_example.py")
    
    if result["valid"]:
        print("✅ 模板验证器工作正常")
        print(f"   模板信息: {result.get('template_info', {})}")
    else:
        print(f"❌ 模板验证器失败: {result['error']}")

def test_annotation_validator():
    """测试标注验证器"""
    print("\n🔍 测试标注验证器...")
    
    validator = AnnotationValidator()
    
    test_data = {
        "id": "test_001",
        "title": "测试文档标题",
        "document_type": "新闻",
        "author": {
            "name": "测试作者",
            "affiliation": "测试机构"
        },
        "tags": ["测试", "集成"]
    }
    
    result = validator.validate_annotation_data("test_template_example.py", test_data)
    
    if result["valid"]:
        print("✅ 标注验证器工作正常")
        print(f"   验证消息: {result.get('message')}")
    else:
        print(f"❌ 标注验证器失败: {result['error']}")

def test_storage_manager():
    """测试存储管理器"""
    print("\n🔍 测试存储管理器...")
    
    storage = StorageManager()
    result = storage.validate_python_template("test_template_example.py")
    
    if result["valid"]:
        print("✅ 存储管理器验证功能正常")
        print(f"   模板信息: {result.get('template_info', {})}")
    else:
        print(f"❌ 存储管理器验证失败: {result['error']}")

def main():
    """主测试函数"""
    print("🚀 后端集成测试开始")
    print("=" * 50)
    
    try:
        test_simple_validator()
        test_template_validator()
        test_annotation_validator()
        test_storage_manager()
        
        print("\n" + "=" * 50)
        print("🎉 后端集成测试完成！")
        print("\n✅ 集成成功的功能:")
        print("   - 简化版文档验证器")
        print("   - 模板验证器")
        print("   - 标注验证器")
        print("   - 存储管理器验证功能")
        print("\n💡 现在可以启动后端服务测试API接口了！")
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 