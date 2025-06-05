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
            print(f"[DEBUG] 开始验证标注数据")
            print(f"[DEBUG] 模板路径: {template_file_path}")
            print(f"[DEBUG] 输入数据: {annotation_data}")
            
            # 获取或创建验证器
            validator = self._get_validator(template_file_path)
            if not validator:
                error_msg = f"无法加载模板文件: {template_file_path}"
                print(f"[ERROR] {error_msg}")
                return {"valid": False, "error": error_msg}
            
            print(f"[DEBUG] 验证器加载成功，主模型: {validator.main_model.__name__ if validator.main_model else 'None'}")
            
            # 验证数据
            result = validator.validate_document(annotation_data)
            print(f"[DEBUG] 验证结果: {result}")
            
            if result["valid"]:
                print(f"[DEBUG] 数据验证通过")
                return {
                    "valid": True,
                    "validated_data": result.get("validated_data", annotation_data),
                    "message": "数据验证通过"
                }
            else:
                # 获取详细错误信息
                errors = result.get("errors", result.get("error_details", []))
                print(f"[DEBUG] 验证失败，原始错误: {errors}")
                
                if isinstance(errors, list):
                    # 格式化验证错误信息
                    error_details = self._format_validation_errors(errors)
                    print(f"[DEBUG] 格式化后的错误: {error_details}")
                    
                    return {
                        "valid": False,
                        "error": "数据验证失败",
                        "error_details": error_details,
                        "raw_errors": errors  # 包含原始错误用于调试
                    }
                else:
                    # 简单错误信息
                    error_msg = str(errors) if errors else result.get("error", "未知验证错误")
                    print(f"[DEBUG] 简单错误信息: {error_msg}")
                    
                    return {
                        "valid": False,
                        "error": error_msg,
                        "error_details": [{"field": "general", "message": error_msg, "type": "validation_error"}]
                    }
                
        except Exception as e:
            error_msg = f"验证过程中发生异常: {str(e)}"
            print(f"[ERROR] {error_msg}")
            import traceback
            print(f"[ERROR] 异常堆栈: {traceback.format_exc()}")
            return {
                "valid": False, 
                "error": error_msg,
                "error_details": [{"field": "system", "message": error_msg, "type": "system_error"}]
            }

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
            print(f"[DEBUG] 获取验证器，模板路径: {template_file_path}")
            
            # 检查缓存
            if template_file_path in self.loaded_validators:
                print(f"[DEBUG] 从缓存中获取验证器")
                return self.loaded_validators[template_file_path]
            
            # 检查文件是否存在
            full_path = Path(template_file_path)
            print(f"[DEBUG] 检查文件是否存在: {full_path.absolute()}")
            
            if not full_path.exists():
                print(f"[ERROR] 模板文件不存在: {full_path.absolute()}")
                return None
            
            print(f"[DEBUG] 模板文件存在，开始创建验证器")
            
            # 创建新的验证器
            validator = SimpleDocumentValidator()
            result = validator.load_template(str(full_path))
            
            print(f"[DEBUG] 验证器加载结果: {result}")
            
            if result["valid"]:
                print(f"[DEBUG] 验证器加载成功，缓存验证器")
                # 缓存验证器
                self.loaded_validators[template_file_path] = validator
                return validator
            else:
                print(f"[ERROR] 验证器加载失败: {result.get('error', '未知错误')}")
                return None
                
        except Exception as e:
            print(f"[ERROR] 获取验证器时发生异常: {str(e)}")
            import traceback
            print(f"[ERROR] 异常堆栈: {traceback.format_exc()}")
            return None
    
    def _format_validation_errors(self, errors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """格式化验证错误信息"""
        formatted_errors = []
        
        for error in errors:
            # 获取字段路径
            loc = error.get("loc", [])
            field_path = ".".join(str(loc_item) for loc_item in loc) if loc else "unknown"
            
            # 获取错误信息
            raw_message = error.get("msg", "")
            error_type = error.get("type", "")
            input_value = error.get("input")
            
            # 确保输入值是可序列化的
            if input_value is not None:
                try:
                    # 尝试转换为字符串，确保可序列化
                    input_value = str(input_value) if input_value is not None else None
                except Exception:
                    input_value = "无法显示"
            
            # 根据错误类型提供更友好的错误信息
            friendly_message = self._get_friendly_error_message(error_type, raw_message, input_value)
            
            formatted_error = {
                "field": field_path,
                "message": str(friendly_message),  # 确保是字符串
                "original_message": str(raw_message),  # 确保是字符串
                "type": str(error_type),  # 确保是字符串
                "input": input_value  # 已经转换为字符串或None
            }
            formatted_errors.append(formatted_error)
            
            print(f"[DEBUG] 格式化错误 - 字段: {field_path}, 消息: {friendly_message}, 类型: {error_type}")
        
        return formatted_errors
    
    def _get_friendly_error_message(self, error_type: str, raw_message: str, input_value: Any) -> str:
        """根据错误类型生成友好的错误信息"""
        
        # 确保所有参数都是字符串
        error_type = str(error_type) if error_type else ""
        raw_message = str(raw_message) if raw_message else ""
        input_display = str(input_value) if input_value is not None else "无"
        
        # 类型转换错误
        if "string_type" in error_type:
            return f"此字段需要文本内容，当前输入: {input_display}"
        elif "int_parsing" in error_type:
            return f"此字段需要整数，当前输入: {input_display}"
        elif "float_parsing" in error_type:
            return f"此字段需要数字，当前输入: {input_display}"
        elif "bool_parsing" in error_type:
            return f"此字段需要是/否值，当前输入: {input_display}"
        
        # 必填字段错误
        elif "missing" in error_type:
            return "此字段为必填项，请填写内容"
        
        # 字符串长度错误
        elif "string_too_short" in error_type:
            return f"内容太短，{raw_message}"
        elif "string_too_long" in error_type:
            return f"内容太长，{raw_message}"
        
        # 数值范围错误
        elif "greater_than_equal" in error_type:
            return f"数值太小，{raw_message}"
        elif "less_than_equal" in error_type:
            return f"数值太大，{raw_message}"
        elif "greater_than" in error_type:
            return f"数值需要大于某个值，{raw_message}"
        elif "less_than" in error_type:
            return f"数值需要小于某个值，{raw_message}"
        
        # 列表相关错误
        elif "list_type" in error_type:
            return f"此字段需要列表格式，当前输入: {input_display}"
        elif "too_short" in error_type and "list" in str(input_value):
            return f"列表项目太少，{raw_message}"
        elif "too_long" in error_type and "list" in str(input_value):
            return f"列表项目太多，{raw_message}"
        
        # 字典/对象错误
        elif "dict_type" in error_type:
            return f"此字段需要对象格式，当前输入: {input_display}"
        
        # 自定义验证错误（通常是业务逻辑错误）
        elif "value_error" in error_type:
            # 对于业务逻辑错误，直接使用原始消息，因为它们通常已经是中文
            if "Value error," in raw_message:
                return raw_message.replace("Value error, ", "")
            return raw_message
        
        # 枚举值错误
        elif "literal_error" in error_type:
            return f"无效的选项值，{raw_message}"
        elif "enum" in error_type:
            return f"请选择有效的选项，{raw_message}"
        
        # 默认返回原始消息，但添加提示
        else:
            return f"{raw_message} (错误类型: {error_type})"

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