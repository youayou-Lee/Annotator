from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.user import User
import enum
from datetime import datetime

class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REVIEWED = "reviewed"
    REJECTED = "rejected"

class FieldType(str, enum.Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    EMAIL = "email"
    PHONE = "phone"
    ENUM = "enum"
    OBJECT = "object"
    ARRAY = "array"

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    annotator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 新增字段
    annotation_fields = Column(JSON, nullable=True)  # 存储需要标注的字段定义，包括字段名称、类型和其他属性
    validation_template = Column(String(255), nullable=True)  # Python模板文件路径，用于校验
    validation_schema = Column(JSON, nullable=True)  # Pydantic BaseModel的JSON表示，用于格式校验
    
    user = relationship("User", back_populates="tasks", foreign_keys=[annotator_id])
    document = relationship("Document", back_populates="tasks")
    annotations = relationship("Annotation", back_populates="task", cascade="all, delete-orphan") 