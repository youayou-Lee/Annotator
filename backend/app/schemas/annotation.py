from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from app.models.annotation import AnnotationType, AnnotationStatus

class AnnotationBase(BaseModel):
    task_id: int
    annotator_id: int
    annotation_type: AnnotationType
    content: Dict[str, Any]
    status: AnnotationStatus = AnnotationStatus.PENDING
    conflict_with: Optional[int] = None

class AnnotationCreate(AnnotationBase):
    pass

class AnnotationBatchCreate(BaseModel):
    annotations: List[AnnotationCreate]

class AnnotationReviewBase(BaseModel):
    annotation_id: int
    reviewer_id: int
    status: AnnotationStatus
    comment: Optional[str] = None

class AnnotationReviewCreate(AnnotationReviewBase):
    pass

class AnnotationReviewUpdate(BaseModel):
    status: Optional[AnnotationStatus] = None
    comment: Optional[str] = None

class AnnotationReview(AnnotationReviewBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AnnotationUpdate(BaseModel):
    task_id: Optional[int] = None
    annotator_id: Optional[int] = None
    annotation_type: Optional[AnnotationType] = None
    content: Optional[Dict[str, Any]] = None
    status: Optional[AnnotationStatus] = None
    conflict_with: Optional[int] = None
    reviewer_id: Optional[int] = None

class AnnotationInDB(AnnotationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Annotation(AnnotationInDB):
    reviewer_id: Optional[int] = None
    
    class Config:
        from_attributes = True 