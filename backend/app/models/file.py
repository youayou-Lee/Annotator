from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from enum import Enum


class FileType(str, Enum):
    """文件类型枚举"""
    DOCUMENT = "documents"
    TEMPLATE = "templates"
    EXPORT = "exports"


class FileInfo(BaseModel):
    """文件信息模型"""
    id: str
    filename: str
    file_path: str
    file_type: FileType
    file_size: int
    uploader_id: str
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


class FileUpload(BaseModel):
    """文件上传响应模型"""
    file_id: str
    filename: str
    file_path: str
    message: str


class FilePreview(BaseModel):
    """文件预览模型"""
    filename: str
    content: str
    file_type: str 