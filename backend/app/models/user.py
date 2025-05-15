from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    tasks = relationship("Task", back_populates="user", foreign_keys="Task.annotator_id")
    annotations = relationship("Annotation", back_populates="annotator", foreign_keys="[Annotation.annotator_id]")
    reviewed_annotations = relationship("Annotation", back_populates="reviewer", foreign_keys="[Annotation.reviewer_id]")
    documents = relationship("Document", back_populates="uploader")
    annotation_history = relationship("AnnotationHistory", back_populates="user")
    annotation_reviews = relationship("AnnotationReview", back_populates="reviewer")
    export_tasks = relationship("ExportTask", back_populates="user") 