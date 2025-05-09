from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, model_validator
from datetime import datetime
import enum, os, json


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskType(str, enum.Enum):
    ANNOTATION = "annotation"
    AI_REVIEW = "ai_review"
    COMPARISON = "comparison"
    TRAINING = "training"

class Task(BaseModel):
    """标注任务模型"""
    id: str = Field(..., description="任务唯一标识")
    name: str = Field(..., description="任务名称")
    description: str = Field(..., description="任务描述")
    files_path: List[str] = Field(..., description="文件存储路径")
    document_ids: List[str] = Field(default_factory=list, description="关联的文书ID列表")
    status: str = Field(default="pending", description="任务状态")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    config: List[Dict[str, Any]] = Field(default_factory=list, description="任务配置，包含字段路径和类型")
    annotations_paths: List[str] = Field(default_factory=list, description="标注结果的保存路径列表")

    def __init__(self,**data):
        super().__init__(**data)


class FieldConfig(BaseModel):
    """字段配置模型"""
    key: str = Field(..., description="字段名称")
    type: str = Field(..., description="字段类型", pattern="^(string|boolean|number|array)$")
    paths: List[str] = Field(default_factory=list, description="字段在文档中的所有可能路径")
    description: str = Field(default="", description="字段描述")
    isMultiple: bool = Field(default=False, description="是否是多值字段")
    minValue: Optional[int] = Field(default=None, description="最小值（仅当类型为number时有效）")
    maxValue: Optional[int] = Field(default=None, description="最大值（仅当类型为number时有效）")

class TaskConfig(BaseModel):
    """任务配置模型"""
    fields: List[FieldConfig] = Field(default_factory=list, description="待标注的字段配置")

    def get_beMarked(self) -> List[Dict[str, Any]]:
        """获取待标注的字段配置列表"""
        result = []
        for field in self.fields:
            field_data = {
                "key": field.key,
                "type": field.type,
                "isMultiple": field.isMultiple,
                "paths": field.paths,
                "description": field.description
            }              
            if field.type == "number":
                # 直接传递原始的最小值和最大值
                field_data["minValue"] = field.minValue
                field_data["maxValue"] = field.maxValue
            result.append(field_data)
        return result

    def set_default_template(self) -> List[Dict[str, Any]]:
        """加载默认模板，并为数字类型字段设置默认范围"""
        with open("data/task_templates/template.json", "r", encoding="utf-8") as f:
            template_data = json.load(f)["need_be_marked_list"]
        
        for field_item in template_data:
            if field_item.get("type") == "number":
                field_item.setdefault("minValue", 0)
                field_item.setdefault("maxValue", 100)
        return template_data

    @model_validator(mode="after")
    def set_default_fields(self) -> "TaskConfig":
        if not self.fields:
            template = self.set_default_template()
            self.fields = [FieldConfig(**item) for item in template]
        return self

    def find_key_paths(self, data: Any, key: str, current_path: str = "") -> List[str]:
        """
        递归查找 key 在 JSON 数据中的所有路径

        Args:
            data: JSON 数据
            key: 要查找的 key
            current_path: 当前路径

        Returns:
            List[str]: key 的所有路径列表
        """
        paths = []
        if isinstance(data, dict):
            for k, v in data.items():
                new_path = f"{current_path}.{k}" if current_path else k
                if k == key:
                    paths.append(new_path)
                paths.extend(self.find_key_paths(v, key, new_path))
        elif isinstance(data, list):
            for i, item in enumerate(data):
                new_path = f"{current_path}[{i}]"
                paths.extend(self.find_key_paths(item, key, new_path))
        return paths

    def update_field_paths(self, json_data: Dict[str, Any]) -> None:
        """
        更新所有 FieldConfig 的 paths 字段，根据其在 JSON 数据中的所有可能路径

        Args:
            json_data: JSON 数据
        """
        for field in self.fields:
            paths = self.find_key_paths(json_data, field.key)
            if paths:
                field.paths = paths
                field.isMultiple = len(paths) > 1