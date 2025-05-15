from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base_class import Base  # 统一Base来源
from app.models.user import User  # 确保 User 被导入

class DocumentStatus(str, enum.Enum):
    PENDING = "pending"  # 待处理
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 处理失败

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)  # 文件大小（字节）
    file_type = Column(String, nullable=False)  # 文件类型（扩展名）
    status = Column(Enum(DocumentStatus), default=DocumentStatus.PENDING)
    error_message = Column(String, nullable=True)  # 处理失败时的错误信息
    
    # 关联字段
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploader = relationship(User, back_populates="documents")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tasks = relationship("Task", back_populates="document") 