from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, model_validator
from datetime import datetime
import enum, os, json
from .document import Document


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
    config: List[Dict[str, Any]] = Field(default_factory=list, description="任务配置，包含字段路径和类型")  # 修改为支持字典格式
    annotations: Dict[str, Any] = Field(default_factory=dict, description="标注结果")
    documents: List['Document'] = Field(default_factory=list, description="任务关联的文书List")

    def set_all_documents(self) -> List['Document']:
        """初始化所有文书信息"""
        self.documents = []
        self.document_ids = []  # 重置document_ids
        for file_path in self.files_path:
            file_path = os.path.join("data", "upload", file_path)  # 拼接文件路径
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        # 如果是单个文档，转换为列表
                        data = [data]
                    for item in data:
                        document = Document(**item)
                        self.documents.append(document)
                        # 确保document_ids包含所有文档ID
                        if hasattr(document, 'id') and document.id:
                            self.document_ids.append(document.id)
            except Exception as e:
                raise ValueError(f"读取文件 {file_path} 失败: {str(e)}")
        return self.documents

    def __init__(self,**data):
        super().__init__(**data)
        # 初始化后自动调用set_all_documents
        if self.files_path:  # 如果有文件路径才初始化
            self.set_all_documents()
    

class FieldConfig(BaseModel):
    """字段配置模型"""
    key: str = Field(..., description="字段名称")
    type: str = Field(..., description="字段类型", pattern="^(string|boolean|number|array)$")
    paths: List[str] = Field(default_factory=list, description="字段在文档中的所有可能路径")
    description: str = Field(default="", description="字段描述")
    isMultiple: bool = Field(default=False, description="是否是多值字段")

class TaskConfig(BaseModel):
    """任务配置模型"""
    fields: List[FieldConfig] = Field(default_factory=list, description="待标注的字段配置")

    def get_beMarked(self) -> List[Dict[str, Any]]:
        """获取待标注的字段配置列表"""
        return [{
            "key": field.key,
            "type": field.type,
            "isMultiple": field.isMultiple,
            "paths": field.paths
        } for field in self.fields]

    def set_default_template(self) -> List[Dict[str, Any]]:
        """加载默认模板"""
        with open("data/task_templates/template.json", "r", encoding="utf-8") as f:
            return json.load(f)["need_be_marked_list"]

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