#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模板验证器 - 基于简化版文档校验模块重写
"""

from typing import Dict, Any
from pathlib import Path
from .simple_document_validator import SimpleDocumentValidator


class TemplateValidator:
    """模板验证器"""
    
    def __init__(self):
        """初始化模板验证器"""
        pass
    
    def validate_template_file(self, file_path: str) -> Dict[str, Any]:
        """验证模板文件"""
        try:
            # 检查文件是否存在
            full_path = Path(file_path)
            if not full_path.exists():
                return {"valid": False, "error": "文件不存在"}
            
            # 使用简化版文档验证器进行验证
            validator = SimpleDocumentValidator()
            result = validator.load_template(str(full_path))
            
            if result["valid"]:
                # 返回兼容原版API的格式
                return {
                    "valid": True,
                    "template_info": result.get("template_info", {}),
                    "annotation_fields": result.get("annotation_fields", [])
                }
            else:
                return {
                    "valid": False,
                    "error": result.get("error", "模板验证失败")
                }
                
        except Exception as e:
            return {"valid": False, "error": f"验证失败: {str(e)}"}

# 以下所有方法都已注释，待重写
# 
# def _check_syntax(self, content: str, file_path: str) -> Dict[str, Any]:
#     """检查Python语法"""
#     try:
#         ast.parse(content)
#         return {"valid": True}
#     except SyntaxError as e:
#         return {
#             "valid": False, 
#             "error": f"语法错误 (行 {e.lineno}): {e.msg}"
#         }
# 
# def _load_and_validate_module(self, content: str, file_path: str) -> Dict[str, Any]:
#     """动态加载模块并验证AnnotationSchema结构"""
#     try:
#         # 创建临时文件
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
#             # 验证AnnotationSchema类
#             return self._validate_annotation_schema(module)
#             
#         finally:
#             # 清理临时文件
#             Path(temp_file_path).unlink(missing_ok=True)
#             
#     except Exception as e:
#         return {"valid": False, "error": f"模块加载失败: {str(e)}"}
# 
# def _validate_annotation_schema(self, module) -> Dict[str, Any]:
#     """验证AnnotationSchema类结构"""
#     # 检查是否存在AnnotationSchema类
#     if not hasattr(module, 'AnnotationSchema'):
#         return {"valid": False, "error": "缺少AnnotationSchema类"}
#     
#     schema_class = getattr(module, 'AnnotationSchema')
#     
#     # 验证必需属性
#     required_attrs = ['schema_name', 'version', 'description', 'fields']
#     for attr in required_attrs:
#         if not hasattr(schema_class, attr):
#             return {"valid": False, "error": f"AnnotationSchema缺少{attr}属性"}
#     
#     # 验证属性类型
#     schema_name = getattr(schema_class, 'schema_name')
#     version = getattr(schema_class, 'version')
#     description = getattr(schema_class, 'description')
#     fields = getattr(schema_class, 'fields')
#     
#     if not isinstance(schema_name, str):
#         return {"valid": False, "error": "schema_name必须是字符串"}
#     
#     if not isinstance(version, str):
#         return {"valid": False, "error": "version必须是字符串"}
#     
#     if not isinstance(description, str):
#         return {"valid": False, "error": "description必须是字符串"}
#     
#     # 验证fields是否为BaseModel子类
#     if not (inspect.isclass(fields) and issubclass(fields, BaseModel)):
#         return {"valid": False, "error": "fields必须是BaseModel的子类"}
#     
#     # 验证字段定义
#     fields_validation = self._validate_fields_model(fields)
#     if not fields_validation["valid"]:
#         return fields_validation
#     
#     # 提取字段信息
#     field_info = self._extract_field_info(fields)
#     
#     return {
#         "valid": True,
#         "template_info": {
#             "schema_name": schema_name,
#             "version": version,
#             "description": description
#         },
#         "annotation_fields": field_info
#     }

# 其他所有方法都已注释，包括：
# _get_model_fields, _get_field_info, _validate_fields_model, 
# _is_valid_field_name, _validate_field_type, _validate_ui_widget,
# _get_nesting_level, _extract_field_info, _get_field_type_string,
# _extract_field_constraints 等 