from typing import List, Optional
import logging
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.document import Document, DocumentUpdate
from app.services.document import (
    get_document,
    get_documents,
    create_document,
    update_document,
    delete_document,
    validate_file_type,
    validate_file_size,
    validate_document_content
)
from app.core.security import get_current_user
from app.models.user import User
from app.core.config import settings

# 设置日志记录器
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload-validate", status_code=status.HTTP_200_OK)
async def validate_document(
    *,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    format: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    验证上传的文档内容，但不保存到数据库
    """
    try:
        logger.debug(f"接收到文件上传验证请求: {file.filename}, 格式: {format}")
        
        # 验证文件类型
        if not validate_file_type(file):
            logger.warning(f"不支持的文件类型: {file.filename}")
            return {
                "success": False,
                "message": f"不支持的文件类型。允许的类型: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            }
        
        # 将文件内容读入内存，避免文件指针问题
        content = await file.read()
        file_size = len(content)
        
        # 验证文件大小
        if file_size > settings.MAX_UPLOAD_SIZE:
            logger.warning(f"文件过大: {file_size} 字节, 超过限制: {settings.MAX_UPLOAD_SIZE}")
            return {
                "success": False,
                "message": f"文件大小超过限制。最大允许: {settings.MAX_UPLOAD_SIZE} 字节"
            }
        
        # 重置文件指针
        await file.seek(0)
        
        # 验证文档内容
        logger.debug(f"开始验证文档内容: {file.filename}")
        validation_results = validate_document_content(file, format)
        logger.debug(f"验证完成: {validation_results}")
        
        return {
            "success": True,
            "results": validation_results
        }
    except Exception as e:
        logger.exception(f"文件验证过程中发生异常: {str(e)}")
        return {
            "success": False,
            "message": f"验证过程中发生错误: {str(e)}"
        }

@router.post("/", response_model=Document)
async def upload_document(
    *,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
) -> Document:
    """
    上传文档
    """
    # 文件验证和处理逻辑已移至service层，直接调用create_document
    # 这样可以避免重复验证和文件指针问题
    
    # 创建文档
    return create_document(db=db, file=file, uploader_id=current_user.id)

@router.get("/", response_model=List[Document])
def get_documents(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    uploader_id: Optional[int] = None,
    current_user: User = Depends(get_current_user)
) -> List[Document]:
    """
    获取文档列表
    """
    return get_documents(
        db=db,
        skip=skip,
        limit=limit,
        uploader_id=uploader_id
    )

@router.get("/{document_id}", response_model=Document)
def get_document(
    *,
    db: Session = Depends(get_db),
    document_id: int,
    current_user: User = Depends(get_current_user)
) -> Document:
    """
    获取单个文档
    """
    db_document = get_document(db, document_id=document_id)
    if not db_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )
    return db_document

@router.put("/{document_id}", response_model=Document)
def update_document(
    *,
    db: Session = Depends(get_db),
    document_id: int,
    document_in: DocumentUpdate,
    current_user: User = Depends(get_current_user)
) -> Document:
    """
    更新文档
    """
    db_document = update_document(
        db=db,
        document_id=document_id,
        document_in=document_in
    )
    if not db_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )
    return db_document

@router.delete("/{document_id}", response_model=Document)
def delete_document(
    *,
    db: Session = Depends(get_db),
    document_id: int,
    current_user: User = Depends(get_current_user)
) -> Document:
    """
    删除文档
    """
    db_document = delete_document(db=db, document_id=document_id)
    if not db_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )
    return db_document