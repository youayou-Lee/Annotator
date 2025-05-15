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

class AnnotationStatus(str, enum.Enum):
    PENDING = "pending"  # 待审核
    APPROVED = "approved"  # 已通过
    REJECTED = "rejected"  # 已拒绝
    CONFLICT = "conflict"  # 存在冲突

class Annotation(Base):
    __tablename__ = "annotations"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    annotator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 审核人ID
    annotation_type = Column(Enum(AnnotationType), nullable=False)
    content = Column(JSON, nullable=False)
    status = Column(Enum(AnnotationStatus), default=AnnotationStatus.PENDING, nullable=False)
    conflict_with = Column(Integer, ForeignKey("annotations.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    task = relationship("Task", back_populates="annotations")
    annotator = relationship("User", back_populates="annotations", foreign_keys=[annotator_id])
    reviewer = relationship("User", back_populates="reviewed_annotations", foreign_keys=[reviewer_id])  # 审核人关系
    history = relationship("AnnotationHistory", back_populates="annotation")
    conflicting_annotation = relationship("Annotation", remote_side=[id], backref="conflicted_by")
    reviews = relationship("AnnotationReview", back_populates="annotation") 