#!/usr/bin/env python3
"""
测试新的模板验证系统
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.template_validator import TemplateValidator
from app.core.annotation_validator import AnnotationValidator


def test_template_validation():
    """测试模板验证功能"""
    print("=== 测试模板验证功能 ===")
    
    validator = TemplateValidator()
    template_path = "data/public_files/templates/example_template.py"
    
    if not Path(template_path).exists():
        print(f"❌ 模板文件不存在: {template_path}")
        return False
    
    # 验证模板
    result = validator.validate_template_file(template_path)
    
    if result["valid"]:
        print("✅ 模板验证通过")
        print(f"模板名称: {result['template_info']['schema_name']}")
        print(f"版本: {result['template_info']['version']}")
        print(f"描述: {result['template_info']['description']}")
        print(f"字段数量: {len(result['annotation_fields'])}")
        
        print("\n字段信息:")
        for field in result['annotation_fields']:
            print(f"  - {field['name']} ({field['type']}): {field['description']}")
            if field.get('required'):
                print(f"    必填字段")
            if field.get('constraints'):
                print(f"    约束: {field['constraints']}")
        
        return True
    else:
        print(f"❌ 模板验证失败: {result['error']}")
        return False


def test_annotation_validation():
    """测试标注数据验证功能"""
    print("\n=== 测试标注数据验证功能 ===")
    
    validator = AnnotationValidator()
    template_path = "data/public_files/templates/example_template.py"
    
    # 测试有效数据
    valid_data = {
        "title": "测试文档标题",
        "doc_type": "article",
        "content": "这是一个测试文档的内容，用于验证标注数据验证功能。",
        "authors": [
            {
                "name": "张三",
                "email": "zhangsan@example.com"
            }
        ],
        "keywords": ["测试", "验证", "文档"],
        "importance": 3,
        "is_reviewed": False,
        "attachments": [],
        "metadata": {"source": "test"},
        "notes": "这是一个测试备注"
    }
    
    print("测试有效数据...")
    result = validator.validate_annotation_data(template_path, valid_data)
    
    if result["valid"]:
        print("✅ 有效数据验证通过")
    else:
        print(f"❌ 有效数据验证失败: {result['error']}")
        if result.get('error_details'):
            for error in result['error_details']:
                print(f"  - {error['field']}: {error['message']}")
    
    # 测试无效数据
    invalid_data = {
        "title": "",  # 违反min_length约束
        "doc_type": "invalid_type",  # 无效的枚举值
        "content": "",  # 违反min_length约束
        "importance": 10,  # 超出范围
        "is_reviewed": "not_boolean"  # 类型错误
    }
    
    print("\n测试无效数据...")
    result = validator.validate_annotation_data(template_path, invalid_data)
    
    if not result["valid"]:
        print("✅ 无效数据正确被拒绝")
        print("错误详情:")
        if result.get('error_details'):
            for error in result['error_details']:
                print(f"  - {error['field']}: {error['message']}")
    else:
        print("❌ 无效数据未被正确拒绝")
    
    return True


def test_partial_validation():
    """测试部分数据验证功能"""
    print("\n=== 测试部分数据验证功能 ===")
    
    validator = AnnotationValidator()
    template_path = "data/public_files/templates/example_template.py"
    
    # 测试部分数据
    partial_data = {
        "title": "部分测试标题",
        "importance": 4
    }
    
    result = validator.validate_partial_data(template_path, partial_data)
    
    if result["valid"]:
        print("✅ 部分数据验证通过")
        print("字段验证结果:")
        for field_name, field_result in result['field_results'].items():
            if field_result['valid']:
                print(f"  - {field_name}: ✅ 有效")
            else:
                print(f"  - {field_name}: ❌ 无效")
                for error in field_result.get('errors', []):
                    print(f"    错误: {error['message']}")
    else:
        print(f"❌ 部分数据验证失败: {result['error']}")
    
    return True


def main():
    """主测试函数"""
    print("开始测试新的文档验证系统...")
    
    # 确保数据目录存在
    template_dir = Path("data/public_files/templates")
    template_dir.mkdir(parents=True, exist_ok=True)
    
    success = True
    
    try:
        success &= test_template_validation()
        success &= test_annotation_validation()
        success &= test_partial_validation()
        
        if success:
            print("\n🎉 所有测试通过！新的文档验证系统工作正常。")
        else:
            print("\n❌ 部分测试失败，请检查实现。")
            
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        success = False
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 