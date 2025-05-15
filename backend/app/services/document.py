import os
import shutil
from typing import Optional, List
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.models.document import Document, DocumentStatus
from app.schemas.document import DocumentCreate, DocumentUpdate
from app.core.config import settings
import uuid
from fastapi import HTTPException

def get_document(db: Session, document_id: int) -> Optional[Document]:
    return db.query(Document).filter(Document.id == document_id).first()

def get_documents(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    uploader_id: Optional[int] = None
) -> List[Document]:
    query = db.query(Document)
    if uploader_id is not None:
        query = query.filter(Document.uploader_id == uploader_id)
    return query.offset(skip).limit(limit).all()

def create_document(
    db: Session,
    *,
    file: UploadFile,
    uploader_id: int
) -> Document:
    # 验证文件类型
    if not validate_file_type(file):
        raise HTTPException(status_code=400, detail="不支持的文件类型")
    
    # 验证文件大小（先读取内存流长度）
    file.file.seek(0, 2)  # 移动到文件末尾
    file_size = file.file.tell()
    file.file.seek(0)     # 复位
    if not validate_file_size(file_size):
        raise HTTPException(status_code=400, detail="文件大小超出限制")
    
    # 生成唯一文件名
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # 确保上传目录存在
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # 保存文件
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 获取文件大小（磁盘实际大小）
    file_size = os.path.getsize(file_path)
    
    # 创建文档记录
    db_document = Document(
        filename=unique_filename,
        original_filename=file.filename,
        file_path=file_path,
        file_size=file_size,
        file_type=file_extension,
        uploader_id=uploader_id
    )
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def update_document(
    db: Session,
    *,
    document_id: int,
    document_in: DocumentUpdate
) -> Optional[Document]:
    db_document = get_document(db, document_id)
    if not db_document:
        return None
    
    update_data = document_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_document, field, value)
    
    db.commit()
    db.refresh(db_document)
    return db_document

def delete_document(db: Session, document_id: int) -> Optional[Document]:
    db_document = get_document(db, document_id)
    if not db_document:
        return None
    
    # 删除文件
    if os.path.exists(db_document.file_path):
        os.remove(db_document.file_path)
    
    # 删除数据库记录
    db.delete(db_document)
    db.commit()
    return db_document

def validate_file_type(file: UploadFile) -> bool:
    """验证文件类型是否允许"""
    file_extension = os.path.splitext(file.filename)[1].lower().lstrip('.')
    return file_extension in settings.ALLOWED_EXTENSIONS

def validate_file_size(file_size: int) -> bool:
    """验证文件大小是否在限制范围内"""
    return file_size <= settings.MAX_UPLOAD_SIZE 