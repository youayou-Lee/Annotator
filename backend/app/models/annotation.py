from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Enum, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import enum
from datetime import datetime

class AnnotationType(str, enum.Enum):
    TEXT = "text"  # 文本标注
    IMAGE = "image"  # 图像标注
    AUDIO = "audio"  # 音频标注
    VIDEO = "video"  # 视频标注

class Annotation(Base):
    __tablename__ = "annotations"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    annotator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    annotation_type = Column(Enum(AnnotationType), nullable=False)
    content = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    task = relationship("Task", back_populates="annotations")
    annotator = relationship("User", back_populates="annotations") 