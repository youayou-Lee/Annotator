from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String, unique=True, index=True)
    content = Column(JSON)
    status = Column(String)  # raw, processed, annotated
    is_annotated = Column(Boolean, default=False)
    is_ai_reviewed = Column(Boolean, default=False)
    is_training_ready = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    task = relationship("Task", back_populates="documents")
    
    # 元数据字段
    court = Column(String)  # 法院
    case_type = Column(String)  # 案件类型
    case_number = Column(String)  # 案号
    judgment_date = Column(DateTime)  # 判决日期
    
    # 标注相关字段
    annotation_data = Column(JSON)  # 标注数据
    ai_review_data = Column(JSON)  # AI审查数据
    training_data = Column(JSON)  # 训练数据
    
    # 关联标注任务
    annotations = relationship("Annotation", back_populates="document")

class Annotation(Base):
    __tablename__ = "annotations"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    annotator_id = Column(Integer, ForeignKey("users.id"))
    content = Column(JSON)
    status = Column(String)  # pending, completed, reviewed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    document = relationship("Document", back_populates="annotations")
    annotator = relationship("User", back_populates="annotations")

class Document(BaseModel):
    """文书数据模型"""
    id: str = Field(..., description="文书唯一标识")
    content: Dict[str, Any] = Field(..., description="文书内容")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    status: str = Field(default="pending", description="文书状态")
    annotations: Dict[str, Any] = Field(default_factory=dict, description="标注信息")
    
    class Config:
        arbitrary_types_allowed = True 