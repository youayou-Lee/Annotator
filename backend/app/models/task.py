from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from enum import Enum


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class DocumentStatus(str, Enum):
    """文档状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskDocument(BaseModel):
    """任务文档模型"""
    id: str
    filename: str
    file_path: str
    status: DocumentStatus = DocumentStatus.PENDING


class TaskTemplate(BaseModel):
    """任务模板模型"""
    filename: str
    file_path: str


class TaskBase(BaseModel):
    """任务基础模型"""
    name: str
    description: Optional[str] = None


class TaskCreate(TaskBase):
    """创建任务模型"""
    assignee_id: Optional[str] = None
    documents: List[str] = []  # 文档文件路径列表
    template_path: Optional[str] = None


class TaskUpdate(BaseModel):
    """更新任务模型"""
    name: Optional[str] = None
    description: Optional[str] = None
    assignee_id: Optional[str] = None
    status: Optional[TaskStatus] = None


class Task(TaskBase):
    """任务响应模型"""
    id: str
    creator_id: str
    assignee_id: Optional[str] = None
    status: TaskStatus
    created_at: datetime
    documents: List[TaskDocument] = []
    template: Optional[TaskTemplate] = None
    
    class Config:
        from_attributes = True 