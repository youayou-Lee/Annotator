from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, validator
from enum import Enum


class FileType(str, Enum):
    """文件类型枚举"""
    DOCUMENT = "documents"
    TEMPLATE = "templates"
    EXPORT = "exports"
    ANNOTATION_RESULT = "annotation_results"


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
    file_size: int
    file_type: FileType
    message: str


class FilePreview(BaseModel):
    """文件预览模型"""
    filename: str
    content: str
    file_type: str
    file_size: int


class FileListResponse(BaseModel):
    """文件列表响应模型"""
    files: List[FileInfo]
    total: int
    file_type: Optional[FileType] = None


class FileDeleteResponse(BaseModel):
    """文件删除响应模型"""
    success: bool
    message: str
    file_id: str


class TemplateValidationResponse(BaseModel):
    """模板验证响应模型"""
    valid: bool
    error: Optional[str] = None
    template_info: Optional[Dict[str, Any]] = None
    annotation_fields: Optional[List[Dict[str, Any]]] = None


class BatchFileUpload(BaseModel):
    """批量文件上传响应模型"""
    successful_uploads: List[FileUpload]
    failed_uploads: List[Dict[str, str]]
    total_uploaded: int
    total_failed: int


class FileDownloadInfo(BaseModel):
    """文件下载信息模型"""
    filename: str
    file_path: str
    file_size: int
    content_type: str 