#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标注数据验证器 - 基于简化版文档校验模块重写
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
from .simple_document_validator import SimpleDocumentValidator


class AnnotationValidator:
    """标注数据验证器"""
    
    def __init__(self):
        """初始化标注验证器"""
        self.loaded_validators = {}  # 缓存已加载的验证器
    
    def validate_annotation_data(self, template_file_path: str, annotation_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证标注数据是否符合模板定义"""
        try:
            # 获取或创建验证器
            validator = self._get_validator(template_file_path)
            if not validator:
                return {"valid": False, "error": "无法加载模板"}
            
            # 验证数据
            result = validator.validate_document(annotation_data)
            
            if result["valid"]:
                return {
                    "valid": True,
                    "validated_data": result.get("validated_data", annotation_data),
                    "message": "数据验证通过"
                }
            else:
                # 格式化验证错误信息
                error_details = self._format_validation_errors(result.get("errors", []))
                return {
                    "valid": False,
                    "error": "数据验证失败",
                    "error_details": error_details
                }
                
        except Exception as e:
            return {"valid": False, "error": f"验证失败: {str(e)}"}

    def validate_partial_data(self, template_file_path: str, partial_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证部分数据（用于实时验证）"""
        try:
            # 获取或创建验证器
            validator = self._get_validator(template_file_path)
            if not validator:
                return {"valid": False, "error": "无法加载模板"}
            
            # 验证部分数据
            result = validator.validate_partial_data(partial_data)
            
            return {
                "valid": result["valid"],
                "error": result.get("error"),
                "field_results": result.get("field_results", {})
            }
                
        except Exception as e:
            return {"valid": False, "error": f"部分验证失败: {str(e)}"}

    def get_template_info(self, template_file_path: str) -> Optional[Dict[str, Any]]:
        """获取模板信息"""
        try:
            validator = self._get_validator(template_file_path)
            if validator and validator.main_model:
                return {
                    "schema_name": validator.main_model.__name__,
                    "version": "1.0",
                    "description": getattr(validator.main_model, '__doc__', '') or '',
                    "annotation_fields": validator.get_annotation_schema()
                }
            return None
        except Exception:
            return None

    def clear_cache(self):
        """清理缓存"""
        self.loaded_validators.clear()
    
    def _get_validator(self, template_file_path: str) -> Optional[SimpleDocumentValidator]:
        """获取或创建验证器"""
        try:
            # 检查缓存
            if template_file_path in self.loaded_validators:
                return self.loaded_validators[template_file_path]
            
            # 检查文件是否存在
            full_path = Path(template_file_path)
            if not full_path.exists():
                return None
            
            # 创建新的验证器
            validator = SimpleDocumentValidator()
            result = validator.load_template(str(full_path))
            
            if result["valid"]:
                # 缓存验证器
                self.loaded_validators[template_file_path] = validator
                return validator
            else:
                return None
                
        except Exception:
            return None
    
    def _format_validation_errors(self, errors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """格式化验证错误信息"""
        formatted_errors = []
        
        for error in errors:
            formatted_error = {
                "field": ".".join(str(loc) for loc in error.get("loc", [])),
                "message": error.get("msg", ""),
                "type": error.get("type", ""),
                "input": error.get("input")
            }
            formatted_errors.append(formatted_error)
        
        return formatted_errors

# 以下所有方法都已注释，待重写
# 
# def _load_template_schema(self, template_file_path: str):
#     """加载模板的Fields类"""
#     try:
#         # 检查缓存
#         if template_file_path in self.loaded_schemas:
#             return self.loaded_schemas[template_file_path]
#         
#         full_path = Path(template_file_path)
#         if not full_path.exists():
#             return None
#         
#         # 读取文件内容
#         with open(full_path, 'r', encoding='utf-8') as f:
#             content = f.read()
#         
#         # 创建临时文件并加载模块
#         with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as temp_file:
#             temp_file.write(content)
#             temp_file_path = temp_file.name
#         
#         try:
#             # 动态加载模块
#             spec = importlib.util.spec_from_file_location("template_module", temp_file_path)
#             module = importlib.util.module_from_spec(spec)
#             spec.loader.exec_module(module)
#             
#             # 获取AnnotationSchema类
#             if hasattr(module, 'AnnotationSchema'):
#                 annotation_schema = getattr(module, 'AnnotationSchema')
#                 if hasattr(annotation_schema, 'fields'):
#                     fields_class = annotation_schema.fields
#                     # 缓存结果
#                     self.loaded_schemas[template_file_path] = fields_class
#                     return fields_class
#             
#             return None
#             
#         finally:
#             # 清理临时文件
#             Path(temp_file_path).unlink(missing_ok=True)
#             
#     except Exception as e:
#         print(f"加载模板失败: {str(e)}")
#         return None
# 
# def _format_validation_errors(self, errors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#     """格式化验证错误信息"""
#     formatted_errors = []
#     
#     for error in errors:
#         formatted_error = {
#             "field": ".".join(str(loc) for loc in error.get("loc", [])),
#             "message": error.get("msg", ""),
#             "type": error.get("type", ""),
#             "input": error.get("input")
#         }
#         formatted_errors.append(formatted_error)
#     
#     return formatted_errors
# 
# 其他所有方法都已注释，包括：
# _get_model_fields, _get_field_info 等 