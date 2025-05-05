import json
import importlib.util
import sys
from pathlib import Path
from typing import Type, Dict, Any, List, Optional, Union
from pydantic import BaseModel, ValidationError
from pydantic_core import PydanticUndefined, PydanticCustomError
class JsonChecker:
    def __init__(self, model_file: Optional[Path] = None, default_model: Optional[Type[BaseModel]] = None):
        """
        初始化校验器
        
        :param model_file: 用户提供的Pydantic模型文件路径
        :param default_model: 默认的Pydantic模型类（当用户未提供模型文件时使用）
        """
        self.model = default_model
        if model_file is not None:
            self.model = self._load_model_from_pyfile(model_file)
        elif default_model is None:
            raise ValueError("必须提供模型文件或默认模型")

    def _load_model_from_pyfile(self, file_path: Path) -> Type[BaseModel]:
        """从Python文件中加载Pydantic模型"""
        module_name = f"user_model_{file_path.stem}"
        
        # 动态加载模块
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None:
            raise ImportError(f"无法从文件 {file_path} 加载模块")
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        
        # 查找所有BaseModel子类
        models = []
        for name, obj in vars(module).items():
            if isinstance(obj, type) and issubclass(obj, BaseModel) and obj is not BaseModel:
                models.append(obj)
        
        if not models:
            raise ValueError("Python文件中未找到有效的Pydantic模型")
        
        return models[0]

    def validate(self, json_data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        校验JSON数据是否符合模型

        :param json_data: 要校验的JSON数据（单个对象或列表）
        :return: 校验通过的数据列表
        :raises: ValidationError 当数据不符合模型时
        """
        if not isinstance(json_data, list):
            json_data = [json_data]

        validated_data = []
        for item in json_data:
            try:
                validated_item = self.model.model_validate(item).model_dump()
                validated_data.append(validated_item)
            except ValidationError as e:
                # 格式化错误信息，指出具体错误位置
                errors = []
                for error in e.errors():
                    loc = "->".join(str(x) for x in error['loc'])
                    errors.append(f"字段 '{loc}': {error['msg']} (类型: {error['type']})")
                # 使用 Pydantic v2 的方式抛出错误
                raise PydanticCustomError(
                    "validation_error",
                    "校验失败:\n" + "\n".join(errors),
                    {"errors": errors}
                )

        return validated_data
    def fill_template(self, json_data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        将JSON数据填充到模板中

        :param json_data: 要填充的JSON数据（单个对象或列表）
        :return: 填充后的数据列表
        """
        if not isinstance(json_data, list):
            json_data = [json_data]

        filled_data = []
        for item in json_data:
            # 获取模型字段及其信息
            model_fields = self.model.__fields__
            filled_item = {}

            for field_name, field_info in model_fields.items():
                # 获取字段类型和默认值
                field_type = field_info.annotation
                default_value = field_info.default

                # 处理未定义默认值的情况
                if default_value == PydanticUndefined:
                    default_value = self._get_default_for_type(field_type)

                # 尝试从用户数据中获取值
                if field_name in item:
                    user_value = item[field_name]
                    # 检查类型是否匹配
                    try:
                        # 跳过 Any 类型的检查
                        if field_type is not Any:
                            # 更健壮的类型检查
                            expected_type = field_type

                            # 处理 Optional 类型
                            if hasattr(field_type, "__origin__") and field_type.__origin__ is Union:
                                expected_type = field_type.__args__[0]  # 取第一个非None类型

                            # 检查类型
                            if not isinstance(user_value, expected_type):
                                # 尝试类型转换
                                try:
                                    user_value = expected_type(user_value)
                                except (TypeError, ValueError):
                                    # 类型转换失败，使用默认值
                                    filled_item[field_name] = default_value
                                    continue

                        filled_item[field_name] = user_value
                    except Exception:
                        # 类型检查失败，使用默认值
                        filled_item[field_name] = default_value
                else:
                    # 字段不存在于用户数据中，使用默认值
                    filled_item[field_name] = default_value

            filled_data.append(filled_item)

        return filled_data

    def _get_default_for_type(self, field_type: Type) -> Any:
        """根据字段类型返回合理的默认值，保留嵌套结构"""
        # 处理 Optional/Union 类型
        if hasattr(field_type, "__origin__") and field_type.__origin__ is Union:
            # 取第一个非None类型
            for t in field_type.__args__:
                if t is not type(None):  # noqa
                    return self._get_default_for_type(t)
            return None

        # 处理泛型容器类型
        if hasattr(field_type, "__origin__"):
            origin_type = field_type.__origin__

            if origin_type is list:
                element_type = field_type.__args__[0] if field_type.__args__ else str
                return [self._get_default_for_type(element_type)]

            elif origin_type is dict:
                key_type = field_type.__args__[0] if len(field_type.__args__) > 0 else str
                value_type = field_type.__args__[1] if len(field_type.__args__) > 1 else Any
                return {self._get_default_for_type(key_type): self._get_default_for_type(value_type)}

            # 其他泛型类型
            try:
                return origin_type()
            except Exception:
                return None

        # 基本类型默认值
        if field_type is str:
            return ""
        elif field_type is int:
            return 0
        elif field_type is float:
            return 0.0
        elif field_type is bool:
            return False
        elif field_type is list:
            return [""]
        elif field_type is dict:
            return {}

        # 处理嵌套Pydantic模型
        try:
            if isinstance(field_type, type) and issubclass(field_type, BaseModel):
                # 递归创建嵌套模型的默认结构
                nested_default = {}
                for name, model_field in field_type.model_fields.items():  # 注意这里改为 model_fields
                    nested_default[name] = self._get_default_for_type(model_field.annotation)  # 使用 annotation 而不是 type_
                return nested_default
        except TypeError:
            pass

        # 默认返回None
        return None
    def process_file(self, json_file: Path, mode: str = 'validate') -> List[Dict[str, Any]]:
        """
        处理JSON/JSONL文件
        
        :param json_file: JSON/JSONL文件路径
        :param mode: 处理模式 ('validate' 或 'fill')
        :return: 处理后的数据列表
        """
        # 读取JSON/JSONL文件
        data = []
        with open(json_file, 'r', encoding='utf-8') as f:
            if json_file.suffix == '.jsonl':
                for line in f:
                    if line.strip():
                        data.append(json.loads(line))
            else:
                file_data = json.load(f)
                if isinstance(file_data, list):
                    data.extend(file_data)
                else:
                    data.append(file_data)
        
        # 根据模式处理数据
        if mode == 'validate':
            return self.validate(data)
        elif mode == 'fill':
            return self.fill_template(data)
        else:
            raise ValueError(f"未知模式: {mode}")
