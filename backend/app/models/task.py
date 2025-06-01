from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
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
    file_size: Optional[int] = None
    created_at: Optional[datetime] = None


class TaskTemplate(BaseModel):
    """任务模板模型"""
    filename: str
    file_path: str
    fields: Optional[Dict[str, Any]] = None  # 模板解析出的字段信息
    validation_result: Optional[Dict[str, Any]] = None  # 模板验证结果


class TaskProgress(BaseModel):
    """任务进度模型"""
    total_documents: int
    completed_documents: int
    in_progress_documents: int
    pending_documents: int
    completion_percentage: float


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


class TaskQuery(BaseModel):
    """任务查询参数"""
    status: Optional[TaskStatus] = None
    assignee_id: Optional[str] = None
    creator_id: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    search: Optional[str] = None  # 搜索任务名称或描述


class Task(TaskBase):
    """任务响应模型"""
    id: str
    creator_id: str
    assignee_id: Optional[str] = None
    status: TaskStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    documents: List[TaskDocument] = []
    template: Optional[TaskTemplate] = None
    progress: Optional[TaskProgress] = None
    
    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """任务列表响应模型"""
    tasks: List[Task]
    total: int
    page: int
    page_size: int
    total_pages: int


class TaskStatistics(BaseModel):
    """任务统计模型"""
    total_tasks: int
    pending_tasks: int
    in_progress_tasks: int
    completed_tasks: int
    my_tasks: int  # 分配给当前用户的任务数 