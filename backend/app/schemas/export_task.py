from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.export_task import ExportStatus, ExportFormat

class ExportTaskBase(BaseModel):
    """导出任务基本属性"""
    description: Optional[str] = Field(None, description="导出任务描述")
    format: ExportFormat = Field(default=ExportFormat.JSON, description="导出格式")

class ExportTaskCreate(ExportTaskBase):
    """创建导出任务"""
    user_id: int = Field(..., description="用户ID")
    task_ids: Optional[list[int]] = Field(None, description="要导出的任务ID列表")
    annotation_ids: Optional[list[int]] = Field(None, description="要导出的标注ID列表")

class ExportTaskUpdate(BaseModel):
    """更新导出任务"""
    status: Optional[ExportStatus] = Field(None, description="导出状态")
    progress: Optional[float] = Field(None, description="导出进度(0-100)")
    file_path: Optional[str] = Field(None, description="导出文件路径")
    error_message: Optional[str] = Field(None, description="错误信息")
    completed_at: Optional[datetime] = Field(None, description="完成时间")

class ExportTaskInDB(ExportTaskBase):
    """数据库中的导出任务"""
    id: int
    user_id: int
    status: ExportStatus
    progress: float
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ExportTask(ExportTaskInDB):
    """导出任务响应模型"""
    pass 