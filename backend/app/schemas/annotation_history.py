from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class AnnotationHistoryBase(BaseModel):
    annotation_id: Optional[int] = None
    user_id: int
    action: str
    content: Dict[str, Any]

class AnnotationHistoryCreate(AnnotationHistoryBase):
    pass

class AnnotationHistoryInDB(AnnotationHistoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class AnnotationHistory(AnnotationHistoryInDB):
    pass 