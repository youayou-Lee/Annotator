import json
import importlib.util
import sys
import random
import string
from pathlib import Path
from typing import Type, Dict, Any, List, Optional, Union
from pydantic import BaseModel, ValidationError
from pydantic_core import PydanticUndefined, PydanticCustomError

def generate_random_id(length: int = 16) -> str:
    """生成指定长度的随机字符串作为ID"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

class JsonChecker:
    def __init__(
        self,
        model_file: Optional[Path],
    ):
        if model_file is not None:
            self.model = self._load_model_from_pyfile(model_file)  # 传递 model_name
        else:
            raise ValueError("必须提供模型文件")
        
        # 验证模型是否包含id字段
        self._validate_model_has_id()
        
    def _validate_model_has_id(self):
        """验证模型是否包含id字段 (Pydantic v2)"""
        if "id" not in self.model.model_fields:
            # 不强制要求模型包含id字段，将在填充模板时自动添加
            print(f"提示: 模型 {self.model.__name__} 没有id字段，将在填充模板时自动添加")

    def _load_model_from_pyfile(
        self, 
        file_path: Path, 
    ) -> Type[BaseModel]:
        """从Python文件中加载指定名称的Pydantic模型"""
        module_name = f"user_model_{file_path.stem}"
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None:
            raise ImportError(f"无法从文件 {file_path} 加载模块")
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        # 查找所有BaseModel子类
        models = [
            obj for name, obj in vars(module).items()
            if (isinstance(obj, type) and 
                issubclass(obj, BaseModel) and 
                obj is not BaseModel)
        ]
        # 如果只有一个模型，直接返回
        if len(models) == 1:
            return models[0]

        # 如果有多个模型，优先返回名为"Document"的模型
        if len(models) > 1:
            for model in models:
                if model.__name__ == "Document":
                    return model

    def validate(self, json_data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        校验JSON数据是否符合模型

        :param json_data: 要校验的JSON数据（单个对象或列表）
        :return: 校验通过的数据列表
        :raises: ValidationError 当数据不符合模型时
        """
        if not isinstance(json_data, list):
            json_data = [json_data]

        # 验证每个项目是否包含id字段且不为空
        for item in json_data:
            if "id" not in item or not item["id"]:
                raise PydanticCustomError(
                    "id_validation_error",
                    "每个数据项必须包含非空的id字段",
                    {"field": "id"}
                )

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
        将JSON数据填充到模板中 (Pydantic v2)

        :param json_data: 要填充的JSON数据（单个对象或列表）
        :return: 填充后的数据列表
        """
        if not isinstance(json_data, list):
            json_data = [json_data]

        filled_data = []
        for item in json_data:
            # 检查id字段是否存在且不为空，否则生成随机id
            if "id" not in item or not item["id"]:
                item["id"] = generate_random_id(16)
                
            # 获取模型字段及其信息
            model_fields = self.model.model_fields
            filled_item = {}

            # 添加id字段（如果模型中没有）
            if "id" not in model_fields:
                filled_item["id"] = item.get("id", generate_random_id(16))

            # 填充模型字段
            for field_name, field_info in model_fields.items():
                # 获取字段类型和默认值
                field_type = field_info.annotation
                default_value = field_info.default

                # 处理未定义默认值的情况
                if default_value == PydanticUndefined:
                    default_value = self._get_default_for_type(field_type)
                
                # 确保id字段不为空
                if field_name == "id" and (default_value is None or default_value == ""):
                    default_value = generate_random_id(16)

                # 尝试从用户数据中获取值
                if field_name in item:
                    user_value = item[field_name]
                    # 特殊处理id字段，如果为空则生成随机id
                    if field_name == "id" and (user_value is None or user_value == ""):
                        user_value = generate_random_id(16)
                        
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
        """根据字段类型返回合理的默认值，保留嵌套结构 (Pydantic v2)"""
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

        # 处理嵌套Pydantic模型 (Pydantic v2)
        try:
            if isinstance(field_type, type) and issubclass(field_type, BaseModel):
                # 递归创建嵌套模型的默认结构
                nested_default = {}
                # Pydantic v2
                for name, model_field in field_type.model_fields.items():
                    nested_default[name] = self._get_default_for_type(model_field.annotation)
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

def formatting_verrification(json_file: Path, temp_py:Path, mode: str = 'validate') -> List[Dict[str, Any]]:
    """
    校验JSON/JSONL文件格式
    
    :param json_file: JSON/JSONL文件路径
    :param temp_file: 模板文件路径
    :param mode: 处理模式 ('validate' 或 'fill')
    :return: 处理后的数据列表
    """
    checker = JsonChecker(model_file=Path(temp_py))

    return checker.process_file(Path(temp_jsonl), mode=mode)