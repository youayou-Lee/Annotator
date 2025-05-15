from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.document import DocumentStatus

class DocumentBase(BaseModel):
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    file_type: str
    status: DocumentStatus = DocumentStatus.PENDING
    error_message: Optional[str] = None

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    status: Optional[DocumentStatus] = None
    error_message: Optional[str] = None

class DocumentInDB(DocumentBase):
    id: int
    uploader_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Document(DocumentInDB):
    pass 