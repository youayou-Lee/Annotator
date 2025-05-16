import os
import shutil
import logging
from typing import Optional, List
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.models.document import Document, DocumentStatus
from app.schemas.document import DocumentCreate, DocumentUpdate
from app.core.config import settings
import uuid
from fastapi import HTTPException

# 设置日志记录器
logger = logging.getLogger(__name__)

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
    
    # 读取文件内容到内存中，避免文件指针问题
    content = file.file.read()
    
    # 验证文件大小
    file_size = len(content)
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
        buffer.write(content)
    
    # 使用内存中计算的文件大小，确保一致性
    # 允许空文件上传（file_size可以为0）
    
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
    # 确保文件名存在
    if not file.filename:
        return False
        
    file_extension = os.path.splitext(file.filename)[1].lower().lstrip('.')
    # 允许空文件，只要扩展名正确
    return file_extension in settings.ALLOWED_EXTENSIONS

def validate_file_size(file_size: int) -> bool:
    """
    验证文件大小是否在允许范围内
    """
    return file_size <= settings.MAX_UPLOAD_SIZE

def validate_document_content(file: UploadFile, format: Optional[str] = None) -> List[dict]:
    """
    验证文档内容是否符合要求
    返回验证结果列表
    """
    try:
        logger.debug(f"开始验证文件: {file.filename}，指定格式: {format}")
        
        # 确保文件存在且可读
        if not file or not file.file:
            logger.error("文件对象为空或文件流不可用")
            return [{
                "success": False,
                "fileName": file.filename if file and file.filename else "未知文件",
                "errors": [{"message": "文件对象为空或文件流不可用"}]
            }]
            
        # 检查文件扩展名
        file_extension = ""
        if file.filename:
            file_extension = os.path.splitext(file.filename)[1].lower().lstrip('.')
        
        # 如果提供了format参数，优先使用format
        effective_format = format if format else file_extension
        logger.debug(f"使用格式: {effective_format}，文件扩展名: {file_extension}")
        
        # 读取文件内容进行验证 - 这里可以根据不同文件格式添加验证逻辑
        content = file.file.read()
        if not content:
            logger.warning(f"文件内容为空: {file.filename}")
        
        # 重置文件指针
        file.file.seek(0)
        
        # 根据不同的文件格式进行专门的验证
        # 这里添加具体的文件格式验证逻辑
        validation_errors = []
        
        # 示例：验证JSON格式
        if effective_format == "json":
            try:
                import json
                json_content = json.loads(content)
                logger.debug(f"JSON解析成功，包含 {len(json_content) if isinstance(json_content, list) else 1} 个项目")
            except json.JSONDecodeError as e:
                logger.error(f"JSON格式验证失败: {str(e)}")
                validation_errors.append({
                    "message": f"JSON格式错误: {str(e)}"
                })
        
        # 返回验证结果
        return [{
            "success": len(validation_errors) == 0,
            "fileName": file.filename,
            "errors": validation_errors
        }]
    except Exception as e:
        logger.exception(f"文件验证过程中发生异常: {str(e)}")
        return [{
            "success": False,
            "fileName": file.filename if file and hasattr(file, 'filename') else "未知文件",
            "errors": [{"message": f"验证过程中发生错误: {str(e)}"}]
        }]