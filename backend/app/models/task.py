from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum, os, json

class LegalBasis(BaseModel):
    """法定刑裁判依据"""
    罪名: str
    构成要件判断: str

class MainPunishment(BaseModel):
    """主刑"""
    管制: Optional[int] = None
    拘役: Optional[int] = None
    有期徒刑: Optional[int] = None
    无期徒刑: Optional[bool] = None
    死刑: Optional[bool] = None

class AdditionalPunishment(BaseModel):
    """附加刑"""
    罚金: Optional[int] = None
    剥夺政治权利: Optional[bool] = None
    没收财产: Optional[str] = None
    驱逐出境: Optional[bool] = None

class JudgmentResult(BaseModel):
    """裁判结果"""
    主刑: MainPunishment
    附加刑: AdditionalPunishment
    是否缓刑: bool
    第一层面量刑调节要素: List[str]
    第二层面量刑调节要素: List[str]
    法定刑区间: str
    与宣告刑是否一致: bool

class JudgmentDetail(BaseModel):
    """裁判详情模型"""
    被告人姓名: str
    法定刑裁判依据: LegalBasis
    裁判结果: JudgmentResult

class Document(BaseModel):
    """文书模型"""
    id: str
    当事人: List[str]
    裁判文书名: str
    案件经过: str
    s25: str
    s26: str
    s27: str
    裁判详情: List[JudgmentDetail]

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
        for file_path in self.files_path:
            file_path = os.path.join("data", "raw", "upload", file_path)  # 拼接文件路径
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        document = Document(**item)
                        self.documents.append(document)
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
        return self.documents

    def __init__(self,**data):
        super().__init__(**data)
        # 初始化后自动调用set_all_documents
        if self.files_path:  # 如果有文件路径才初始化
            self.set_all_documents()
    

class FieldConfig(BaseModel):
    """字段配置模型"""
    name: str = Field(..., description="字段名称")
    type: str = Field(..., description="字段类型", pattern="^(string|boolean|number|array)$")
    path: str = Field(..., description="字段在文档中的路径")
    description: str = Field(default="", description="字段描述")

class TaskConfig(BaseModel):
    """任务配置模型"""
    fields: List[FieldConfig] = Field(..., description="待标注的字段配置")

    def get_beMarked(self) -> List[Dict[str, Any]]:
        """获取待标注的字段配置列表"""
        return [{"path": field.path, "type": field.type} for field in self.fields]

    @classmethod
    def from_template(cls, template_path: str, selected_fields: List[Dict[str, Any]]) -> 'TaskConfig':
        """从模板文件创建配置"""
        with open(template_path, 'r', encoding='utf-8') as f:
            template = json.load(f)
            
        field_configs = []
        for field in selected_fields:
            field_configs.append(FieldConfig(
                name=field["path"].split(".")[-1],
                type=field["type"],
                path=field["path"]
            ))
            
        return cls(fields=field_configs)
