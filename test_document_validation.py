#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文档校验功能
"""

import sys
import os
from pathlib import Path

# 添加后端路径到Python路径
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.core.simple_document_validator import SimpleDocumentValidator

def test_document_validation():
    """测试文档校验功能"""
    print("=== 文档校验功能测试 ===\n")
    
    # 模板文件路径
    template_path = "backend/data/public_files/templates/20250605_122824_test_template.py"
    
    # 有效文档文件路径
    valid_document_path = "backend/data/public_files/documents/20250605_123812_test_template.json"
    
    # 无效文档文件路径
    invalid_document_path = "backend/data/public_files/documents/test_invalid_data.json"
    
    try:
        print(f"1. 加载模板文件: {template_path}")
        
        # 检查文件是否存在
        if not Path(template_path).exists():
            print(f"❌ 模板文件不存在: {template_path}")
            return False
        
        # 创建验证器并加载模板
        validator = SimpleDocumentValidator(template_path)
        print("✅ 模板加载成功")
        
        # 测试有效文档
        print(f"\n2. 测试有效文档: {valid_document_path}")
        if Path(valid_document_path).exists():
            result = validator.validate_file(valid_document_path)
            print(f"   总计文档数: {result.get('total', 0)}")
            print(f"   有效文档数: {result.get('valid_count', 0)}")
            print(f"   无效文档数: {result.get('invalid_count', 0)}")
            
            if result.get('invalid_count', 0) == 0:
                print("✅ 有效文档校验通过")
            else:
                print("❌ 有效文档校验失败")
        else:
            print(f"❌ 有效文档文件不存在: {valid_document_path}")
        
        # 测试无效文档
        print(f"\n3. 测试无效文档: {invalid_document_path}")
        if Path(invalid_document_path).exists():
            result = validator.validate_file(invalid_document_path)
            print(f"   总计文档数: {result.get('total', 0)}")
            print(f"   有效文档数: {result.get('valid_count', 0)}")
            print(f"   无效文档数: {result.get('invalid_count', 0)}")
            
            if result.get('invalid_count', 0) > 0:
                print(f"\n4. 错误详情:")
                for i, error_result in enumerate(result.get('results', [])):
                    if not error_result.get('valid'):
                        print(f"   第 {i+1} 条记录错误:")
                        print(f"     错误信息: {error_result.get('error', '未知错误')}")
                        
                        if 'error_details' in error_result:
                            for field_error in error_result['error_details']:
                                field_path = ".".join(str(loc) for loc in field_error.get('loc', []))
                                print(f"     字段 '{field_path}': {field_error.get('msg', '')}")
                
                print("✅ 无效文档错误检测成功")
            else:
                print("❌ 无效文档应该有错误但未检测到")
        else:
            print(f"❌ 无效文档文件不存在: {invalid_document_path}")
        
        print(f"\n5. 测试API校验错误格式化:")
        
        # 模拟API的错误处理逻辑
        def format_validation_error(validation_result):
            """格式化校验错误信息（模拟API逻辑）"""
            if validation_result.get("invalid_count", 0) > 0:
                error_message = "文档数据校验失败，请检查以下文件："
                doc_error = {
                    'file_path': invalid_document_path,
                    'total_documents': validation_result.get("total", 0),
                    'invalid_count': validation_result.get("invalid_count", 0),
                    'errors': []
                }
                
                # 提取具体的错误信息
                for result in validation_result.get("results", []):
                    if not result.get("valid"):
                        error_info = {
                            "index": result.get("index", 0),
                            "message": result.get("error", "未知错误")
                        }
                        
                        # 如果有详细的字段错误信息
                        if "error_details" in result:
                            error_info["field_errors"] = []
                            for field_error in result["error_details"]:
                                error_info["field_errors"].append({
                                    "field": ".".join(str(loc) for loc in field_error.get("loc", [])),
                                    "message": field_error.get("msg", ""),
                                    "type": field_error.get("type", "")
                                })
                        
                        doc_error["errors"].append(error_info)
                
                error_message += f"\n\n文件: {doc_error['file_path']}"
                error_message += f"\n总计: {doc_error['total_documents']} 条记录，其中 {doc_error['invalid_count']} 条有错误"
                
                for error in doc_error['errors'][:3]:  # 只显示前3个错误
                    error_message += f"\n  - 第 {error['index'] + 1} 条记录: {error['message']}"
                    if 'field_errors' in error:
                        for field_error in error['field_errors'][:2]:  # 只显示前2个字段错误
                            error_message += f"\n    字段 '{field_error['field']}': {field_error['message']}"
                
                if len(doc_error['errors']) > 3:
                    error_message += f"\n  ... 还有 {len(doc_error['errors']) - 3} 个错误"
                
                return error_message
            return None
        
        if Path(invalid_document_path).exists():
            result = validator.validate_file(invalid_document_path)
            formatted_error = format_validation_error(result)
            if formatted_error:
                print("   格式化后的错误信息:")
                print(formatted_error)
                print("✅ 错误信息格式化成功")
        
        return True
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_document_validation()
    if success:
        print("\n🎉 文档校验功能测试成功！")
    else:
        print("\n💥 文档校验功能测试失败！") 