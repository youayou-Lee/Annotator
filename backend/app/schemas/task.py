from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from app.models.task import TaskStatus, FieldType

class AnnotationFieldDef(BaseModel):
    name: str
    label: str
    type: FieldType
    required: bool = True
    description: Optional[str] = None
    enum_values: Optional[List[str]] = None  # 如果type是ENUM，则需要提供可选值
    default: Optional[Any] = None
    min: Optional[Union[int, float]] = None  # 数字类型的最小值
    max: Optional[Union[int, float]] = None  # 数字类型的最大值
    regex: Optional[str] = None  # 字符串类型的正则表达式验证

class TaskBase(BaseModel):
    document_id: int
    annotator_id: int
    reviewer_id: Optional[int] = None
    user_id: int
    status: TaskStatus = TaskStatus.PENDING
    title: str
    description: Optional[str] = None
    annotation_fields: Optional[List[AnnotationFieldDef]] = None
    validation_template: Optional[str] = None
    validation_schema: Optional[Dict[str, Any]] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    status: Optional[TaskStatus] = None
    reviewer_id: Optional[int] = None
    annotation_fields: Optional[List[AnnotationFieldDef]] = None
    validation_template: Optional[str] = None
    validation_schema: Optional[Dict[str, Any]] = None

class TaskInDB(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Task(TaskInDB):
    pass 