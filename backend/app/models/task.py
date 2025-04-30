from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum

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

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    type = Column(Enum(TaskType))
    template = Column(JSON)  # 标注模板
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    priority = Column(Integer, default=0)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 任务配置
    config = Column(JSON)  # 任务配置，包括过滤条件、标注字段等
    editable_fields = Column(JSON)  # 可编辑字段列表
    validation_rules = Column(JSON)  # 验证规则
    
    # 关联
    documents = relationship("Document", back_populates="task")
    creator = relationship("User", back_populates="tasks")
    
    # 统计信息
    total_documents = Column(Integer, default=0)
    annotated_documents = Column(Integer, default=0)
    ai_reviewed_documents = Column(Integer, default=0)
    training_ready_documents = Column(Integer, default=0)

class TaskDocument(Base):
    __tablename__ = "task_documents"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    document_id = Column(Integer, ForeignKey("documents.id"))
    status = Column(String)  # pending, in_progress, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    task = relationship("Task", back_populates="documents")
    document = relationship("Document")

class Task(BaseModel):
    """标注任务模型"""
    id: str = Field(..., description="任务唯一标识")
    name: str = Field(..., description="任务名称")
    description: str = Field(..., description="任务描述")
    document_ids: List[str] = Field(default_factory=list, description="关联的文书ID列表")
    status: str = Field(default="pending", description="任务状态")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    config: Dict[str, Any] = Field(default_factory=dict, description="任务配置")
    annotations: Dict[str, Any] = Field(default_factory=dict, description="标注结果")
    documents: List[Document] = Field(default_factory=list, description="任务关联的文书列表")
    
    class Config:
        arbitrary_types_allowed = True 