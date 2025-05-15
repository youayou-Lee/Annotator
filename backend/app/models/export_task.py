from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from app.db.base_class import Base
from datetime import datetime

class ExportStatus(str, PyEnum):
    """导出任务状态"""
    PENDING = "pending"      # 等待中
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 失败

class ExportFormat(str, PyEnum):
    """导出格式"""
    JSON = "json"
    JSONL = "jsonl"
    CSV = "csv"
    EXCEL = "excel"

class ExportTask(Base):
    """导出任务模型"""
    __tablename__ = "export_tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    description = Column(String(255), nullable=True)
    status = Column(Enum(ExportStatus), default=ExportStatus.PENDING, nullable=False)
    progress = Column(Float, default=0.0, nullable=False)  # 0-100的百分比
    format = Column(Enum(ExportFormat), default=ExportFormat.JSON, nullable=False)
    file_path = Column(String(255), nullable=True)  # 导出文件的路径
    error_message = Column(String(255), nullable=True)  # 如果失败，错误信息
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)  # 完成时间
    
    # 关系
    user = relationship("User", back_populates="export_tasks") 