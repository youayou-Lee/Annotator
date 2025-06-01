from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum


class AnnotationStatus(str, Enum):
    """标注状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REVIEWED = "reviewed"


class AnnotationBase(BaseModel):
    """标注基础模型"""
    annotation_data: Dict[str, Any] = {}


class AnnotationCreate(AnnotationBase):
    """创建标注模型"""
    pass


class AnnotationUpdate(BaseModel):
    """更新标注模型"""
    annotation_data: Optional[Dict[str, Any]] = None
    status: Optional[AnnotationStatus] = None


class Annotation(AnnotationBase):
    """标注响应模型"""
    document_id: str
    task_id: str
    status: AnnotationStatus = AnnotationStatus.PENDING
    annotator_id: Optional[str] = None
    reviewer_id: Optional[str] = None
    updated_at: datetime = None
    reviewed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AnnotationSubmit(BaseModel):
    """提交标注模型"""
    annotation_data: Dict[str, Any]


class AnnotationReview(BaseModel):
    """复审标注模型"""
    approved: bool
    review_comments: Optional[str] = None
    revised_data: Optional[Dict[str, Any]] = None 