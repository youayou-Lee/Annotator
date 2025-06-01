import importlib.util
import tempfile
from typing import Dict, Any, List, Optional
from pathlib import Path
from pydantic import BaseModel, ValidationError
import json


class AnnotationValidator:
    """标注数据验证器，验证标注数据是否符合模板定义"""
    
    def __init__(self):
        self.loaded_schemas = {}  # 缓存已加载的模板
    
    def validate_annotation_data(self, template_file_path: str, annotation_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证标注数据是否符合模板定义"""
        try:
            # 加载模板
            schema_class = self._load_template_schema(template_file_path)
            if not schema_class:
                return {"valid": False, "error": "无法加载模板"}
            
            # 验证数据
            try:
                # 使用Pydantic模型验证数据
                validated_data = schema_class(**annotation_data)
                # 兼容不同版本的Pydantic
                if hasattr(validated_data, 'model_dump'):
                    data_dict = validated_data.model_dump()
                else:
                    data_dict = validated_data.dict()
                
                return {
                    "valid": True,
                    "validated_data": data_dict,
                    "message": "数据验证通过"
                }
            except ValidationError as e:
                # 格式化验证错误信息
                error_details = self._format_validation_errors(e.errors())
                return {
                    "valid": False,
                    "error": "数据验证失败",
                    "error_details": error_details
                }
            except Exception as e:
                return {"valid": False, "error": f"验证过程中发生错误: {str(e)}"}
                
        except Exception as e:
            return {"valid": False, "error": f"验证失败: {str(e)}"}
    
    def _load_template_schema(self, template_file_path: str):
        """加载模板的Fields类"""
        try:
            # 检查缓存
            if template_file_path in self.loaded_schemas:
                return self.loaded_schemas[template_file_path]
            
            full_path = Path(template_file_path)
            if not full_path.exists():
                return None
            
            # 读取文件内容
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 创建临时文件并加载模块
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            try:
                # 动态加载模块
                spec = importlib.util.spec_from_file_location("template_module", temp_file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # 获取AnnotationSchema类
                if hasattr(module, 'AnnotationSchema'):
                    annotation_schema = getattr(module, 'AnnotationSchema')
                    if hasattr(annotation_schema, 'fields'):
                        fields_class = annotation_schema.fields
                        # 缓存结果
                        self.loaded_schemas[template_file_path] = fields_class
                        return fields_class
                
                return None
                
            finally:
                # 清理临时文件
                Path(temp_file_path).unlink(missing_ok=True)
                
        except Exception as e:
            print(f"加载模板失败: {str(e)}")
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
    
    def get_template_info(self, template_file_path: str) -> Optional[Dict[str, Any]]:
        """获取模板信息"""
        try:
            full_path = Path(template_file_path)
            if not full_path.exists():
                return None
            
            # 读取文件内容
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 创建临时文件并加载模块
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            try:
                # 动态加载模块
                spec = importlib.util.spec_from_file_location("template_module", temp_file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # 获取模板信息
                if hasattr(module, 'AnnotationSchema'):
                    annotation_schema = getattr(module, 'AnnotationSchema')
                    return {
                        "schema_name": getattr(annotation_schema, 'schema_name', ''),
                        "version": getattr(annotation_schema, 'version', ''),
                        "description": getattr(annotation_schema, 'description', '')
                    }
                
                return None
                
            finally:
                # 清理临时文件
                Path(temp_file_path).unlink(missing_ok=True)
                
        except Exception as e:
            print(f"获取模板信息失败: {str(e)}")
            return None
    
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
                'required': field.is_required() if hasattr(field, 'is_required') else True,
                'default': field.default if hasattr(field, 'default') else None
            }
        # Pydantic v1
        elif hasattr(field, 'type_'):
            return {
                'type_': field.type_,
                'required': field.required,
                'default': field.default if field.default is not ... else None
            }
        else:
            return {
                'type_': str,
                'required': True,
                'default': None
            }
    
    def validate_partial_data(self, template_file_path: str, partial_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证部分数据（用于实时验证）"""
        try:
            schema_class = self._load_template_schema(template_file_path)
            if not schema_class:
                return {"valid": False, "error": "无法加载模板"}
            
            # 获取模型字段定义
            model_fields = self._get_model_fields(schema_class)
            
            validation_results = {}
            
            # 逐字段验证
            for field_name, value in partial_data.items():
                if field_name in model_fields:
                    field = model_fields[field_name]
                    field_info = self._get_field_info(field)
                    
                    try:
                        # 创建临时模型只包含当前字段
                        temp_data = {field_name: value}
                        # 为其他必需字段提供默认值
                        for fname, fld in model_fields.items():
                            if fname != field_name:
                                fld_info = self._get_field_info(fld)
                                if fld_info['required']:
                                    if fld_info['type_'] == str:
                                        temp_data[fname] = ""
                                    elif fld_info['type_'] == int:
                                        temp_data[fname] = 0
                                    elif fld_info['type_'] == float:
                                        temp_data[fname] = 0.0
                                    elif fld_info['type_'] == bool:
                                        temp_data[fname] = False
                                    elif fld_info['type_'] == list:
                                        temp_data[fname] = []
                                    elif fld_info['type_'] == dict:
                                        temp_data[fname] = {}
                                    else:
                                        # 尝试使用默认值
                                        if fld_info['default'] is not None:
                                            temp_data[fname] = fld_info['default']
                                        else:
                                            temp_data[fname] = ""
                        
                        validated = schema_class(**temp_data)
                        validation_results[field_name] = {
                            "valid": True,
                            "value": getattr(validated, field_name)
                        }
                    except ValidationError as e:
                        field_errors = [err for err in e.errors() if err.get("loc") and err["loc"][0] == field_name]
                        if field_errors:
                            validation_results[field_name] = {
                                "valid": False,
                                "errors": self._format_validation_errors(field_errors)
                            }
                        else:
                            validation_results[field_name] = {"valid": True, "value": value}
                    except Exception as e:
                        validation_results[field_name] = {
                            "valid": False,
                            "errors": [{"message": str(e)}]
                        }
                else:
                    validation_results[field_name] = {
                        "valid": False,
                        "errors": [{"message": f"字段'{field_name}'在模板中未定义"}]
                    }
            
            return {
                "valid": True,
                "field_results": validation_results
            }
            
        except Exception as e:
            return {"valid": False, "error": f"部分验证失败: {str(e)}"}
    
    def clear_cache(self):
        """清空模板缓存"""
        self.loaded_schemas.clear() 