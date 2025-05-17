from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import enum
from datetime import datetime

class UserRole(enum.Enum):
    superuser = "superuser"
    admin = "admin"
    annotator = "annotator"

class UserStatus(enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # 时间戳字段
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    
    # 新增字段
    role = Column(Enum(UserRole), default=UserRole.annotator, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.pending, nullable=False)
    approval_date = Column(DateTime, nullable=True)
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # 关系
    approved_by = relationship("User", remote_side=[id], foreign_keys=[approved_by_id])
    approved_users = relationship("User", back_populates="approved_by", foreign_keys=[approved_by_id])
    
    tasks = relationship("Task", back_populates="user", foreign_keys="Task.annotator_id")
    annotations = relationship("Annotation", back_populates="annotator", foreign_keys="[Annotation.annotator_id]")
    reviewed_annotations = relationship("Annotation", back_populates="reviewer", foreign_keys="[Annotation.reviewer_id]")
    documents = relationship("Document", back_populates="uploader")
    annotation_history = relationship("AnnotationHistory", back_populates="user")
    annotation_reviews = relationship("AnnotationReview", back_populates="reviewer")
    export_tasks = relationship("ExportTask", back_populates="user") 