import ast
import importlib.util
import sys
import tempfile
from typing import Dict, Any, List, Optional, Union, get_type_hints, get_origin, get_args
from pathlib import Path
from pydantic import BaseModel, Field
from enum import Enum
import inspect
import re


class TemplateValidator:
    """模板验证器，按照文档指南验证AnnotationSchema格式的模板"""
    
    def __init__(self):
        self.supported_ui_widgets = {
            "text", "textarea", "select", "radio", "checkbox", 
            "date-picker", "time-picker", "color-picker", 
            "tag-input", "monaco-editor"
        }
    
    def validate_template_file(self, file_path: str) -> Dict[str, Any]:
        """验证模板文件"""
        try:
            full_path = Path(file_path)
            if not full_path.exists():
                return {"valid": False, "error": "文件不存在"}
            
            # 读取文件内容
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 基本语法检查
            syntax_result = self._check_syntax(content, str(full_path))
            if not syntax_result["valid"]:
                return syntax_result
            
            # 动态加载模块并验证结构
            module_result = self._load_and_validate_module(content, str(full_path))
            if not module_result["valid"]:
                return module_result
            
            return module_result
            
        except Exception as e:
            return {"valid": False, "error": f"验证失败: {str(e)}"}
    
    def _check_syntax(self, content: str, file_path: str) -> Dict[str, Any]:
        """检查Python语法"""
        try:
            ast.parse(content)
            return {"valid": True}
        except SyntaxError as e:
            return {
                "valid": False, 
                "error": f"语法错误 (行 {e.lineno}): {e.msg}"
            }
    
    def _load_and_validate_module(self, content: str, file_path: str) -> Dict[str, Any]:
        """动态加载模块并验证AnnotationSchema结构"""
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            try:
                # 动态加载模块
                spec = importlib.util.spec_from_file_location("template_module", temp_file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # 验证AnnotationSchema类
                return self._validate_annotation_schema(module)
                
            finally:
                # 清理临时文件
                Path(temp_file_path).unlink(missing_ok=True)
                
        except Exception as e:
            return {"valid": False, "error": f"模块加载失败: {str(e)}"}
    
    def _validate_annotation_schema(self, module) -> Dict[str, Any]:
        """验证AnnotationSchema类结构"""
        # 检查是否存在AnnotationSchema类
        if not hasattr(module, 'AnnotationSchema'):
            return {"valid": False, "error": "缺少AnnotationSchema类"}
        
        schema_class = getattr(module, 'AnnotationSchema')
        
        # 验证必需属性
        required_attrs = ['schema_name', 'version', 'description', 'fields']
        for attr in required_attrs:
            if not hasattr(schema_class, attr):
                return {"valid": False, "error": f"AnnotationSchema缺少{attr}属性"}
        
        # 验证属性类型
        schema_name = getattr(schema_class, 'schema_name')
        version = getattr(schema_class, 'version')
        description = getattr(schema_class, 'description')
        fields = getattr(schema_class, 'fields')
        
        if not isinstance(schema_name, str):
            return {"valid": False, "error": "schema_name必须是字符串"}
        
        if not isinstance(version, str):
            return {"valid": False, "error": "version必须是字符串"}
        
        if not isinstance(description, str):
            return {"valid": False, "error": "description必须是字符串"}
        
        # 验证fields是否为BaseModel子类
        if not (inspect.isclass(fields) and issubclass(fields, BaseModel)):
            return {"valid": False, "error": "fields必须是BaseModel的子类"}
        
        # 验证字段定义
        fields_validation = self._validate_fields_model(fields)
        if not fields_validation["valid"]:
            return fields_validation
        
        # 提取字段信息
        field_info = self._extract_field_info(fields)
        
        return {
            "valid": True,
            "template_info": {
                "schema_name": schema_name,
                "version": version,
                "description": description
            },
            "annotation_fields": field_info
        }
    
    def _get_model_fields(self, model_class):
        """获取模型字段，兼容不同版本的Pydantic"""
        # Pydantic v2
        if hasattr(model_class, 'model_fields'):
            return model_class.model_fields
        # Pydantic v1
        elif hasattr(model_class, '__fields__'):
            return model_class.__fields__
        else:
            return {}
    
    def _get_field_info(self, field):
        """获取字段信息，兼容不同版本的Pydantic"""
        # Pydantic v2
        if hasattr(field, 'annotation'):
            return {
                'type_': field.annotation,
                'required': field.is_required(),
                'default': field.default if hasattr(field, 'default') else None,
                'description': field.description if hasattr(field, 'description') else None
            }
        # Pydantic v1
        elif hasattr(field, 'type_'):
            return {
                'type_': field.type_,
                'required': field.required,
                'default': field.default if field.default is not ... else None,
                'description': field.field_info.description if hasattr(field, 'field_info') and hasattr(field.field_info, 'description') else None
            }
        else:
            return {
                'type_': str,
                'required': True,
                'default': None,
                'description': None
            }
    
    def _validate_fields_model(self, fields_class) -> Dict[str, Any]:
        """验证Fields模型的字段定义"""
        try:
            # 获取字段定义
            model_fields = self._get_model_fields(fields_class)
            
            if not model_fields:
                return {"valid": False, "error": "Fields模型没有定义任何字段"}
            
            # 验证每个字段
            for field_name, field in model_fields.items():
                # 检查字段命名规范
                if not self._is_valid_field_name(field_name):
                    return {
                        "valid": False, 
                        "error": f"字段名'{field_name}'不符合命名规范，应使用小驼峰或下划线命名法"
                    }
                
                # 获取字段信息
                field_info = self._get_field_info(field)
                
                # 检查是否有描述
                if not field_info['description']:
                    return {
                        "valid": False, 
                        "error": f"字段'{field_name}'缺少描述信息"
                    }
                
                # 验证字段类型
                field_type_validation = self._validate_field_type(field_name, field_info)
                if not field_type_validation["valid"]:
                    return field_type_validation
                
                # 验证UI控件配置
                ui_widget_validation = self._validate_ui_widget(field_name, field)
                if not ui_widget_validation["valid"]:
                    return ui_widget_validation
            
            return {"valid": True}
            
        except Exception as e:
            return {"valid": False, "error": f"字段验证失败: {str(e)}"}
    
    def _is_valid_field_name(self, field_name: str) -> bool:
        """检查字段名是否符合命名规范"""
        # 小驼峰命名法或下划线命名法
        camel_case_pattern = r'^[a-z][a-zA-Z0-9]*$'
        snake_case_pattern = r'^[a-z][a-z0-9_]*$'
        
        return (re.match(camel_case_pattern, field_name) is not None or 
                re.match(snake_case_pattern, field_name) is not None)
    
    def _validate_field_type(self, field_name: str, field_info: Dict[str, Any]) -> Dict[str, Any]:
        """验证字段类型"""
        try:
            field_type = field_info['type_']
            
            # 检查是否使用了typing模块的类型
            origin = get_origin(field_type)
            if origin is not None:
                # 处理泛型类型如List[str], Dict[str, Any]等
                args = get_args(field_type)
                if origin in (list, List):
                    if not args:
                        return {
                            "valid": False, 
                            "error": f"字段'{field_name}'的List类型必须指定元素类型，如List[str]"
                        }
                elif origin in (dict, Dict):
                    if len(args) != 2:
                        return {
                            "valid": False, 
                            "error": f"字段'{field_name}'的Dict类型必须指定键值类型，如Dict[str, Any]"
                        }
            
            # 检查嵌套层级（简单检查）
            nesting_level = self._get_nesting_level(field_type)
            if nesting_level > 3:
                return {
                    "valid": False, 
                    "error": f"字段'{field_name}'的嵌套层级过深（超过3层）"
                }
            
            return {"valid": True}
            
        except Exception as e:
            return {"valid": False, "error": f"字段'{field_name}'类型验证失败: {str(e)}"}
    
    def _validate_ui_widget(self, field_name: str, field) -> Dict[str, Any]:
        """验证UI控件配置"""
        try:
            # Pydantic v2
            if hasattr(field, 'json_schema_extra'):
                extra = field.json_schema_extra or {}
                if 'ui_widget' in extra:
                    ui_widget = extra['ui_widget']
                    if ui_widget not in self.supported_ui_widgets:
                        return {
                            "valid": False, 
                            "error": f"字段'{field_name}'指定的UI控件'{ui_widget}'不受支持"
                        }
            # Pydantic v1
            elif hasattr(field, 'field_info') and hasattr(field.field_info, 'extra'):
                extra = field.field_info.extra
                if 'ui_widget' in extra:
                    ui_widget = extra['ui_widget']
                    if ui_widget not in self.supported_ui_widgets:
                        return {
                            "valid": False, 
                            "error": f"字段'{field_name}'指定的UI控件'{ui_widget}'不受支持"
                        }
            
            return {"valid": True}
            
        except Exception as e:
            return {"valid": False, "error": f"字段'{field_name}'UI控件验证失败: {str(e)}"}
    
    def _get_nesting_level(self, field_type, level=0) -> int:
        """获取类型嵌套层级"""
        if level > 5:  # 防止无限递归
            return level
        
        origin = get_origin(field_type)
        if origin is not None:
            args = get_args(field_type)
            if args:
                max_nested_level = level
                for arg in args:
                    nested_level = self._get_nesting_level(arg, level + 1)
                    max_nested_level = max(max_nested_level, nested_level)
                return max_nested_level
        
        return level
    
    def _extract_field_info(self, fields_class) -> List[Dict[str, Any]]:
        """提取字段信息用于前端显示"""
        field_info_list = []
        model_fields = self._get_model_fields(fields_class)
        
        for field_name, field in model_fields.items():
            field_info = self._get_field_info(field)
            
            field_data = {
                "name": field_name,
                "type": self._get_field_type_string(field_info['type_']),
                "required": field_info['required'],
                "description": field_info['description'] or "",
                "default": field_info['default']
            }
            
            # 添加额外的字段信息
            extra = {}
            
            # Pydantic v2
            if hasattr(field, 'json_schema_extra'):
                extra = field.json_schema_extra or {}
            # Pydantic v1
            elif hasattr(field, 'field_info') and hasattr(field.field_info, 'extra'):
                extra = field.field_info.extra
            
            # UI控件
            if 'ui_widget' in extra:
                field_data['ui_widget'] = extra['ui_widget']
            
            # 选择项
            if 'choices' in extra:
                field_data['choices'] = extra['choices']
            
            # 条件显示
            if 'depends_on' in extra:
                field_data['depends_on'] = extra['depends_on']
            
            # 添加验证规则
            constraints = self._extract_field_constraints(field)
            if constraints:
                field_data['constraints'] = constraints
            
            # 添加示例值
            if hasattr(field, 'examples') and field.examples:
                field_data['example'] = field.examples[0]
            elif hasattr(field, 'field_info') and hasattr(field.field_info, 'example'):
                field_data['example'] = field.field_info.example
            
            field_info_list.append(field_data)
        
        return field_info_list
    
    def _get_field_type_string(self, field_type) -> str:
        """获取字段类型的字符串表示"""
        if hasattr(field_type, '__name__'):
            return field_type.__name__
        
        origin = get_origin(field_type)
        if origin is not None:
            args = get_args(field_type)
            if origin in (list, List):
                if args:
                    return f"List[{self._get_field_type_string(args[0])}]"
                return "List"
            elif origin in (dict, Dict):
                if len(args) == 2:
                    return f"Dict[{self._get_field_type_string(args[0])}, {self._get_field_type_string(args[1])}]"
                return "Dict"
            elif origin in (Union,):
                # 处理Optional类型
                if len(args) == 2 and type(None) in args:
                    non_none_type = args[0] if args[1] is type(None) else args[1]
                    return f"Optional[{self._get_field_type_string(non_none_type)}]"
                return f"Union[{', '.join(self._get_field_type_string(arg) for arg in args)}]"
        
        return str(field_type)
    
    def _extract_field_constraints(self, field) -> Dict[str, Any]:
        """提取字段约束信息"""
        constraints = {}
        
        # Pydantic v2
        if hasattr(field, 'constraints'):
            field_constraints = field.constraints
            if field_constraints:
                for constraint_name, constraint_value in field_constraints.items():
                    if constraint_value is not None:
                        constraints[constraint_name] = constraint_value
        
        # Pydantic v1
        elif hasattr(field, 'field_info'):
            field_info_obj = field.field_info
            
            # 字符串长度约束
            if hasattr(field_info_obj, 'min_length') and field_info_obj.min_length is not None:
                constraints['min_length'] = field_info_obj.min_length
            if hasattr(field_info_obj, 'max_length') and field_info_obj.max_length is not None:
                constraints['max_length'] = field_info_obj.max_length
            
            # 数值约束
            if hasattr(field_info_obj, 'gt') and field_info_obj.gt is not None:
                constraints['gt'] = field_info_obj.gt
            if hasattr(field_info_obj, 'ge') and field_info_obj.ge is not None:
                constraints['ge'] = field_info_obj.ge
            if hasattr(field_info_obj, 'lt') and field_info_obj.lt is not None:
                constraints['lt'] = field_info_obj.lt
            if hasattr(field_info_obj, 'le') and field_info_obj.le is not None:
                constraints['le'] = field_info_obj.le
            
            # 正则表达式
            if hasattr(field_info_obj, 'regex') and field_info_obj.regex is not None:
                constraints['regex'] = field_info_obj.regex.pattern if hasattr(field_info_obj.regex, 'pattern') else str(field_info_obj.regex)
        
        return constraints 