#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版文档校验模块
保留核心功能：模板验证、文档验证、标注字段提取
"""

import json
import importlib.util
import ast
from pydantic import BaseModel, ValidationError, Field
from typing import Dict, List, Type, Any, Optional, get_origin, get_args, Union
import inspect
from pathlib import Path

class AnnotationField:
    """标注字段信息"""
    def __init__(self, path: str, field_type: Type, required: bool, 
                 description: str = "", constraints: Dict[str, Any] = None):
        self.path = path
        self.field_type = field_type
        self.required = required
        self.description = description
        self.constraints = constraints or {}

class SimpleDocumentValidator:
    """简化版文档验证器"""
    
    def __init__(self, template_path: str = None):
        self.template_path = template_path
        self.main_model = None
        self.annotation_fields = []
        
        if template_path:
            self.load_template(template_path)
    
    def load_template(self, template_path: str) -> Dict[str, Any]:
        """加载并验证模板文件"""
        try:
            # 1. 检查文件是否存在
            if not Path(template_path).exists():
                return {"valid": False, "error": "模板文件不存在"}
            
            # 2. 语法检查
            syntax_result = self._check_syntax(template_path)
            if not syntax_result["valid"]:
                return syntax_result
            
            # 3. 动态加载模块
            load_result = self._load_module(template_path)
            if not load_result["valid"]:
                return load_result
            
            # 4. 提取标注字段
            self.annotation_fields = self._extract_annotation_fields()
            
            return {
                "valid": True, 
                "main_model": self.main_model.__name__,
                "annotation_fields_count": len(self.annotation_fields)
            }
            
        except Exception as e:
            return {"valid": False, "error": f"模板加载失败: {str(e)}"}
    
    def _check_syntax(self, template_path: str) -> Dict[str, Any]:
        """检查Python文件语法"""
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 使用ast解析检查语法
            ast.parse(content)
            return {"valid": True}
            
        except SyntaxError as e:
            return {
                "valid": False, 
                "error": f"语法错误 (行 {e.lineno}): {e.msg}"
            }
        except Exception as e:
            return {"valid": False, "error": f"文件读取失败: {str(e)}"}
    
    def _load_module(self, template_path: str) -> Dict[str, Any]:
        """动态加载模块并找到主模型"""
        try:
            # 动态导入模块
            spec = importlib.util.spec_from_file_location("template", template_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 查找BaseModel类
            models = []
            main_models = []
            
            for name, obj in module.__dict__.items():
                if (isinstance(obj, type) and 
                    issubclass(obj, BaseModel) and 
                    obj != BaseModel):
                    models.append((name, obj))
                    
                    # 检查是否标记为主模型
                    model_config = getattr(obj, "model_config", {})
                    if hasattr(model_config, 'get'):
                        json_schema_extra = model_config.get("json_schema_extra", {})
                    else:
                        json_schema_extra = getattr(model_config, "json_schema_extra", {})
                    
                    if json_schema_extra.get("is_main_model", False):
                        main_models.append((name, obj))
            
            # 确定主模型
            if len(main_models) == 1:
                self.main_model = main_models[0][1]
            elif len(main_models) > 1:
                return {
                    "valid": False, 
                    "error": f"发现多个主模型: {[name for name, _ in main_models]}"
                }
            elif len(models) == 1:
                # 如果只有一个BaseModel，默认为主模型
                self.main_model = models[0][1]
            else:
                return {"valid": False, "error": "未找到有效的BaseModel类"}
            
            return {"valid": True}
            
        except Exception as e:
            return {"valid": False, "error": f"模块加载失败: {str(e)}"}
    
    def _extract_annotation_fields(self, model: Type[BaseModel] = None, 
                                 prefix: str = "", visited: set = None) -> List[AnnotationField]:
        """递归提取标注字段"""
        if model is None:
            model = self.main_model
        
        if visited is None:
            visited = set()
        
        # 防止循环引用
        if id(model) in visited:
            return []
        visited.add(id(model))
        
        fields = []
        
        # 获取模型字段
        model_fields = getattr(model, 'model_fields', {})
        
        for field_name, field_info in model_fields.items():
            # 构建字段路径
            current_path = f"{prefix}.{field_name}" if prefix else field_name
            
            # 检查是否为标注字段
            json_schema_extra = getattr(field_info, 'json_schema_extra', {}) or {}
            is_annotation = json_schema_extra.get("is_annotation", False)
            
            # 获取字段类型
            field_type = getattr(field_info, 'annotation', None)
            if field_type is None:
                continue
            
            # 处理不同类型的字段
            if self._is_basemodel_type(field_type):
                # 嵌套BaseModel
                nested_fields = self._extract_annotation_fields(
                    field_type, current_path, visited.copy()
                )
                fields.extend(nested_fields)
                
            elif self._is_list_of_basemodel(field_type):
                # List[BaseModel]
                inner_type = get_args(field_type)[0]
                nested_fields = self._extract_annotation_fields(
                    inner_type, f"{current_path}[]", visited.copy()
                )
                fields.extend(nested_fields)
                
            elif self._is_optional_type(field_type):
                # Optional类型处理
                inner_type = self._get_optional_inner_type(field_type)
                if self._is_basemodel_type(inner_type):
                    nested_fields = self._extract_annotation_fields(
                        inner_type, current_path, visited.copy()
                    )
                    fields.extend(nested_fields)
                elif self._is_list_of_basemodel(inner_type):
                    list_inner_type = get_args(inner_type)[0]
                    nested_fields = self._extract_annotation_fields(
                        list_inner_type, f"{current_path}[]", visited.copy()
                    )
                    fields.extend(nested_fields)
                elif is_annotation:
                    # Optional的基础类型标注字段
                    fields.append(self._create_annotation_field(
                        current_path, inner_type, field_info, False
                    ))
                    
            elif is_annotation:
                # 基础类型标注字段
                fields.append(self._create_annotation_field(
                    current_path, field_type, field_info, True
                ))
        
        visited.remove(id(model))
        return fields
    
    def _create_annotation_field(self, path: str, field_type: Type, 
                               field_info: Any, is_required: bool) -> AnnotationField:
        """创建标注字段对象"""
        description = getattr(field_info, 'description', '') or ''
        
        # 提取约束条件
        constraints = {}
        json_schema_extra = getattr(field_info, 'json_schema_extra', {}) or {}
        
        # 从metadata中提取约束
        if hasattr(field_info, 'metadata') and field_info.metadata:
            for constraint in field_info.metadata:
                if hasattr(constraint, 'ge'):
                    constraints['ge'] = constraint.ge
                elif hasattr(constraint, 'le'):
                    constraints['le'] = constraint.le
                elif hasattr(constraint, 'min_length'):
                    constraints['min_length'] = constraint.min_length
                elif hasattr(constraint, 'max_length'):
                    constraints['max_length'] = constraint.max_length
        
        # 检查是否必需
        if hasattr(field_info, 'is_required'):
            is_required = field_info.is_required()
        
        return AnnotationField(
            path=path,
            field_type=field_type,
            required=is_required,
            description=description,
            constraints=constraints
        )
    
    def _is_basemodel_type(self, type_hint: Type) -> bool:
        """检查是否为BaseModel类型"""
        try:
            return (inspect.isclass(type_hint) and 
                    issubclass(type_hint, BaseModel))
        except TypeError:
            return False
    
    def _is_list_of_basemodel(self, type_hint: Type) -> bool:
        """检查是否为List[BaseModel]类型"""
        origin = get_origin(type_hint)
        if origin is list or origin is List:
            args = get_args(type_hint)
            if args and self._is_basemodel_type(args[0]):
                return True
        return False
    
    def _is_optional_type(self, type_hint: Type) -> bool:
        """检查是否为Optional类型"""
        origin = get_origin(type_hint)
        if origin is Union:
            args = get_args(type_hint)
            return len(args) == 2 and type(None) in args
        return False
    
    def _get_optional_inner_type(self, type_hint: Type) -> Type:
        """获取Optional类型的内部类型"""
        args = get_args(type_hint)
        return args[0] if args[1] is type(None) else args[1]
    
    def validate_document(self, data: dict) -> Dict[str, Any]:
        """验证单个文档"""
        if not self.main_model:
            return {"valid": False, "error": "未加载模板"}
        
        try:
            instance = self.main_model(**data)
            return {"valid": True, "instance": instance}
        except ValidationError as e:
            return {"valid": False, "errors": e.errors()}
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """验证JSON/JSONL文件"""
        if not self.main_model:
            return {"valid": False, "error": "未加载模板"}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.endswith('.jsonl'):
                    # JSONL文件处理
                    results = []
                    for line_num, line in enumerate(f, 1):
                        try:
                            data = json.loads(line.strip())
                            result = self.validate_document(data)
                            result['line_number'] = line_num
                            results.append(result)
                        except json.JSONDecodeError as e:
                            results.append({
                                "valid": False,
                                "error": f"JSON格式错误: {e}",
                                "line_number": line_num
                            })
                else:
                    # JSON文件处理
                    data = json.load(f)
                    if isinstance(data, list):
                        results = []
                        for idx, item in enumerate(data):
                            result = self.validate_document(item)
                            result['index'] = idx
                            results.append(result)
                    else:
                        results = [self.validate_document(data)]
            
            valid_count = sum(1 for r in results if r.get("valid"))
            return {
                "total": len(results),
                "valid_count": valid_count,
                "invalid_count": len(results) - valid_count,
                "results": results
            }
            
        except Exception as e:
            return {"valid": False, "error": f"文件处理失败: {str(e)}"}
    
    def extract_annotations(self, data: dict) -> Dict[str, Any]:
        """提取标注字段值"""
        if not self.main_model:
            return {}
        
        try:
            instance = self.main_model(**data)
            return self._extract_values_from_instance(instance)
        except Exception:
            return {}
    
    def _extract_values_from_instance(self, instance: BaseModel, 
                                    prefix: str = "", visited: set = None) -> Dict[str, Any]:
        """从实例中提取标注字段值"""
        if visited is None:
            visited = set()
        
        if id(instance) in visited:
            return {}
        visited.add(id(instance))
        
        values = {}
        model_fields = getattr(instance.__class__, 'model_fields', {})
        
        for field_name, field_info in model_fields.items():
            try:
                value = getattr(instance, field_name)
            except AttributeError:
                continue
            
            current_path = f"{prefix}.{field_name}" if prefix else field_name
            json_schema_extra = getattr(field_info, 'json_schema_extra', {}) or {}
            is_annotation = json_schema_extra.get("is_annotation", False)
            
            if isinstance(value, BaseModel):
                # 嵌套BaseModel
                nested_values = self._extract_values_from_instance(
                    value, current_path, visited.copy()
                )
                values.update(nested_values)
                
            elif isinstance(value, list):
                # 列表处理
                if is_annotation and all(not isinstance(item, BaseModel) for item in value):
                    # 基础类型列表
                    values[current_path] = value
                else:
                    # 包含BaseModel的列表
                    list_values = []
                    nested_dict_values = {}
                    
                    for idx, item in enumerate(value):
                        if isinstance(item, BaseModel):
                            item_values = self._extract_values_from_instance(
                                item, f"{current_path}[{idx}]", visited.copy()
                            )
                            for key, val in item_values.items():
                                clean_key = key.replace(f"{current_path}[{idx}]", f"{current_path}[]")
                                if clean_key not in nested_dict_values:
                                    nested_dict_values[clean_key] = []
                                nested_dict_values[clean_key].append(val)
                        else:
                            list_values.append(item)
                    
                    if is_annotation and list_values:
                        values[current_path] = list_values
                    
                    values.update(nested_dict_values)
                    
            elif is_annotation:
                # 基础类型标注字段
                values[current_path] = value
        
        visited.remove(id(instance))
        return values
    
    def get_annotation_schema(self) -> List[Dict[str, Any]]:
        """获取标注字段模式信息"""
        return [{
            "path": field.path,
            "type": self._get_type_name(field.field_type),
            "required": field.required,
            "description": field.description,
            "constraints": field.constraints
        } for field in self.annotation_fields]
    
    def _get_type_name(self, type_hint: Type) -> str:
        """获取类型名称"""
        if hasattr(type_hint, '__name__'):
            return type_hint.__name__
        else:
            return str(type_hint)

# 使用示例
if __name__ == "__main__":
    # 创建验证器
    validator = SimpleDocumentValidator()
    
    # 加载模板
    result = validator.load_template("template_example.py")
    print("模板加载结果:", result)
    
    if result["valid"]:
        # 获取标注字段信息
        schema = validator.get_annotation_schema()
        print(f"标注字段数量: {len(schema)}")
        
        # 验证示例数据
        sample_data = {
            "id": "test_001",
            "title": "测试文档",
            "content": "这是测试内容"
        }
        
        validation_result = validator.validate_document(sample_data)
        print("文档验证结果:", validation_result)
        
        if validation_result["valid"]:
            # 提取标注字段
            annotations = validator.extract_annotations(sample_data)
            print("提取的标注字段:", annotations) 