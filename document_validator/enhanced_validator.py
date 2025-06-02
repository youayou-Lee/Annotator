import json
import importlib.util
from pydantic import BaseModel, ValidationError
from typing import Dict, List, Type, Any, Optional, get_origin, get_args, Union
import inspect

class AnnotationField:
    """标注字段元数据"""
    def __init__(self, path: str, type_: Type, is_required: bool, 
                 description: str = "", constraints: Dict[str, Any] = None):
        self.path = path  # 字段路径（如 "content_sections[].annotations.sentiment_score"）
        self.type_ = type_  # Python类型
        self.is_required = is_required  # 是否必填
        self.description = description  # 字段描述
        self.constraints = constraints or {}  # 字段约束条件

class EnhancedDocumentValidator:
    def __init__(self, template_path: str):
        self.template_path = template_path
        self.model = self._load_main_model(template_path)
        self.annotation_fields = self._extract_annotation_fields(self.model)
    
    def _load_main_model(self, template_path: str) -> Type[BaseModel]:
        """动态加载模板文件并获取主模型"""
        spec = importlib.util.spec_from_file_location("template", template_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        main_models = []
        all_models = []
        
        # 查找所有BaseModel类
        for name, obj in module.__dict__.items():
            if (isinstance(obj, type) and 
                issubclass(obj, BaseModel) and 
                obj != BaseModel):
                all_models.append((name, obj))
                
                # 检查是否标记为主模型
                model_config = getattr(obj, "model_config", {})
                json_schema_extra = model_config.get("json_schema_extra", {})
                if json_schema_extra.get("is_main_model", False):
                    main_models.append((name, obj))
        
        if len(main_models) == 1:
            return main_models[0][1]
        elif len(main_models) > 1:
            raise ValueError(f"Multiple main models found: {[name for name, _ in main_models]}")
        elif len(all_models) == 1:
            # 如果只有一个BaseModel，默认为主模型
            print(f"Warning: No main model marked, using the only BaseModel: {all_models[0][0]}")
            return all_models[0][1]
        else:
            raise ValueError("No main BaseModel found in template")

    def _extract_annotation_fields(
        self, 
        model: Type[BaseModel], 
        prefix: str = "",
        visited_models: Optional[set] = None
    ) -> List[AnnotationField]:
        """递归提取标注字段，处理循环引用"""
        if visited_models is None:
            visited_models = set()
        
        # 防止循环引用
        model_id = id(model)
        if model_id in visited_models:
            return []
        visited_models.add(model_id)
        
        fields = []
        
        # 使用Pydantic v2的model_fields
        model_fields = model.model_fields
        
        for field_name, field in model_fields.items():
            # 处理字段别名映射
            json_key = getattr(field, 'alias', None) or field_name
            
            # 构建当前字段路径
            current_path = f"{prefix}.{json_key}" if prefix else json_key
            
            # 检查字段标记
            json_schema_extra = getattr(field, 'json_schema_extra', None) or {}
            is_annotation = json_schema_extra.get("is_annotation", False)
            
            # 获取字段类型
            field_type = getattr(field, 'annotation', None)
            if field_type is None:
                continue
            
            # 处理不同类型的字段
            if self._is_basemodel_type(field_type):
                # 直接的BaseModel类型
                nested_fields = self._extract_annotation_fields(
                    field_type, 
                    prefix=current_path,
                    visited_models=visited_models.copy()
                )
                fields.extend(nested_fields)
            
            elif self._is_list_of_basemodel(field_type):
                # List[BaseModel]类型
                inner_type = get_args(field_type)[0]
                nested_fields = self._extract_annotation_fields(
                    inner_type, 
                    prefix=f"{current_path}[]",
                    visited_models=visited_models.copy()
                )
                fields.extend(nested_fields)
            
            elif self._is_optional_basemodel(field_type):
                # Optional[BaseModel]类型
                inner_type = get_args(field_type)[0]
                if self._is_basemodel_type(inner_type):
                    nested_fields = self._extract_annotation_fields(
                        inner_type, 
                        prefix=current_path,
                        visited_models=visited_models.copy()
                    )
                    fields.extend(nested_fields)
                elif self._is_list_of_basemodel(inner_type):
                    # Optional[List[BaseModel]]
                    list_inner_type = get_args(inner_type)[0]
                    nested_fields = self._extract_annotation_fields(
                        list_inner_type, 
                        prefix=f"{current_path}[]",
                        visited_models=visited_models.copy()
                    )
                    fields.extend(nested_fields)
            
            elif is_annotation:
                # 基础类型字段被标记为需要标注
                description = getattr(field, 'description', "") or ""
                
                # 提取约束条件
                constraints = {}
                
                # 从json_schema_extra中提取约束
                for key, value in json_schema_extra.items():
                    if key not in ['is_annotation', 'description']:
                        constraints[key] = value
                
                # 从Field的metadata中提取约束 (Pydantic v2)
                if hasattr(field, 'metadata') and field.metadata:
                    for constraint in field.metadata:
                        if hasattr(constraint, 'ge'):
                            constraints['ge'] = constraint.ge
                        elif hasattr(constraint, 'le'):
                            constraints['le'] = constraint.le
                        elif hasattr(constraint, 'gt'):
                            constraints['gt'] = constraint.gt
                        elif hasattr(constraint, 'lt'):
                            constraints['lt'] = constraint.lt
                        elif hasattr(constraint, 'min_length'):
                            constraints['min_length'] = constraint.min_length
                        elif hasattr(constraint, 'max_length'):
                            constraints['max_length'] = constraint.max_length
                        elif hasattr(constraint, 'pattern'):
                            constraints['pattern'] = constraint.pattern
                        elif hasattr(constraint, 'multiple_of'):
                            constraints['multiple_of'] = constraint.multiple_of
                
                # 检查字段是否必需 (Pydantic v2)
                is_required = field.is_required()
                
                fields.append(AnnotationField(
                    path=current_path,
                    type_=field_type,
                    is_required=is_required,
                    description=description,
                    constraints=constraints
                ))
        
        visited_models.remove(model_id)
        return fields

    def _is_basemodel_type(self, type_hint: Type) -> bool:
        """检查类型是否为BaseModel"""
        try:
            return (inspect.isclass(type_hint) and 
                    issubclass(type_hint, BaseModel))
        except TypeError:
            return False

    def _is_list_of_basemodel(self, type_hint: Type) -> bool:
        """检查类型是否为List[BaseModel]"""
        origin = get_origin(type_hint)
        if origin is list or origin is List:
            args = get_args(type_hint)
            if args and self._is_basemodel_type(args[0]):
                return True
        return False

    def _is_optional_basemodel(self, type_hint: Type) -> bool:
        """检查类型是否为Optional[BaseModel]或Union[BaseModel, None]"""
        origin = get_origin(type_hint)
        if origin is Union:
            args = get_args(type_hint)
            if len(args) == 2 and type(None) in args:
                non_none_type = args[0] if args[1] is type(None) else args[1]
                return (self._is_basemodel_type(non_none_type) or 
                        self._is_list_of_basemodel(non_none_type))
        return False

    def validate_document(self, json_data: dict) -> Dict[str, Any]:
        """验证单个JSON文档"""
        try:
            instance = self.model(**json_data)
            return {"valid": True, "instance": instance}
        except ValidationError as e:
            return {"valid": False, "errors": e.errors()}
    
    def extract_annotations(self, json_data: dict) -> Dict[str, Any]:
        """从验证后的文档中提取标注字段值"""
        try:
            instance = self.model(**json_data)
            return self._extract_values_from_instance(instance)
        except ValidationError as e:
            print(f"Validation error: {e}")
            return {}

    def _extract_values_from_instance(
        self, 
        instance: BaseModel, 
        prefix: str = "",
        visited_instances: Optional[set] = None
    ) -> Dict[str, Any]:
        """从实例中递归提取标注字段值"""
        if visited_instances is None:
            visited_instances = set()
        
        # 防止循环引用
        instance_id = id(instance)
        if instance_id in visited_instances:
            return {}
        visited_instances.add(instance_id)
        
        values = {}
        
        # 使用Pydantic v2的model_fields
        model_fields = instance.__class__.model_fields
        
        for field_name, field in model_fields.items():
            # 获取字段值
            try:
                value = getattr(instance, field_name)
            except AttributeError:
                continue
            
            # 处理字段别名
            json_key = getattr(field, 'alias', None) or field_name
            
            # 构建当前路径
            current_path = f"{prefix}.{json_key}" if prefix else json_key
            
            # 检查是否是标注字段
            json_schema_extra = getattr(field, 'json_schema_extra', None) or {}
            is_annotation = json_schema_extra.get("is_annotation", False)
            
            if isinstance(value, BaseModel):
                # 嵌套BaseModel
                nested_values = self._extract_values_from_instance(
                    value, 
                    prefix=current_path,
                    visited_instances=visited_instances.copy()
                )
                values.update(nested_values)
            
            elif isinstance(value, list):
                # 处理列表
                if is_annotation and all(not isinstance(item, BaseModel) for item in value):
                    # 如果是标注字段且列表中都是基础类型
                    values[current_path] = value
                else:
                    # 处理列表中的BaseModel或混合类型
                    list_values = []
                    nested_dict_values = {}
                    
                    for idx, item in enumerate(value):
                        if isinstance(item, BaseModel):
                            # 列表中的BaseModel
                            item_values = self._extract_values_from_instance(
                                item, 
                                prefix=f"{current_path}[{idx}]",
                                visited_instances=visited_instances.copy()
                            )
                            # 将嵌套字典值合并
                            for key, val in item_values.items():
                                # 移除具体索引，使用[]表示数组
                                clean_key = key.replace(f"{current_path}[{idx}]", f"{current_path}[]")
                                if clean_key not in nested_dict_values:
                                    nested_dict_values[clean_key] = []
                                nested_dict_values[clean_key].append(val)
                        else:
                            list_values.append(item)
                    
                    # 如果当前字段被标记为标注字段且有基础类型值
                    if is_annotation and list_values:
                        values[current_path] = list_values
                    
                    # 添加嵌套字典值
                    values.update(nested_dict_values)
            
            elif is_annotation:
                # 基础类型的标注字段
                values[current_path] = value
        
        visited_instances.remove(instance_id)
        return values

    def get_annotation_schema(self) -> List[Dict[str, Any]]:
        """获取标注字段的完整模式信息"""
        return [{
            "path": field.path,
            "type": self._get_type_name(field.type_),
            "required": field.is_required,
            "description": field.description,
            "constraints": field.constraints
        } for field in self.annotation_fields]

    def _get_type_name(self, type_hint: Type) -> str:
        """获取类型名称"""
        if hasattr(type_hint, '__name__'):
            return type_hint.__name__
        else:
            return str(type_hint)

    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """验证整个JSON/JSONL文件"""
        results = []
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.endswith('.jsonl'):
                for line_num, line in enumerate(f, 1):
                    try:
                        data = json.loads(line)
                        result = self.validate_document(data)
                        result['line_number'] = line_num
                        results.append(result)
                    except json.JSONDecodeError as e:
                        results.append({
                            "valid": False, 
                            "errors": f"Invalid JSON format at line {line_num}: {e}",
                            "line_number": line_num
                        })
            else:
                try:
                    data = json.load(f)
                    if isinstance(data, list):
                        for idx, item in enumerate(data):
                            result = self.validate_document(item)
                            result['index'] = idx
                            results.append(result)
                    else:
                        results.append(self.validate_document(data))
                except json.JSONDecodeError as e:
                    results.append({"valid": False, "errors": f"Invalid JSON format: {e}"})
        
        return {
            "total": len(results),
            "valid_count": sum(1 for r in results if r.get("valid")),
            "invalid_count": sum(1 for r in results if not r.get("valid")),
            "results": results
        }