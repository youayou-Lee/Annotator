from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any
from app.models.annotation import AnnotationType

class AnnotationBase(BaseModel):
    task_id: int
    annotator_id: int
    annotation_type: AnnotationType
    content: Dict[str, Any]

class AnnotationCreate(AnnotationBase):
    pass

class AnnotationUpdate(BaseModel):
    content: Dict[str, Any]

class AnnotationInDB(AnnotationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Annotation(AnnotationInDB):
    pass 