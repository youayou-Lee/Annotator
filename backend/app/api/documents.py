from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
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

router = APIRouter()

@router.post("/upload-validate", status_code=status.HTTP_200_OK)
async def validate_document(
    *,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    format: str = None,
    current_user: User = Depends(get_current_user)
):
    """
    验证上传的文档内容，但不保存到数据库
    """
    # 验证文件类型
    if not validate_file_type(file):
        return {
            "success": False,
            "message": f"不支持的文件类型。允许的类型: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        }
    
    # 验证文件大小
    file_size = 0
    for chunk in file.file:
        file_size += len(chunk)
        if file_size > settings.MAX_UPLOAD_SIZE:
            return {
                "success": False,
                "message": f"文件大小超过限制。最大允许: {settings.MAX_UPLOAD_SIZE} 字节"
            }
    
    # 重置文件指针
    await file.seek(0)
    
    # 验证文档内容
    validation_results = validate_document_content(file, format)
    
    return {
        "success": True,
        "results": validation_results
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
    # 验证文件类型
    if not validate_file_type(file):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型。允许的类型: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # 验证文件大小
    file_size = 0
    for chunk in file.file:
        file_size += len(chunk)
        if file_size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文件大小超过限制。最大允许: {settings.MAX_UPLOAD_SIZE} 字节"
            )
    
    # 重置文件指针
    await file.seek(0)
    
    # 创建文档
    return create_document(db=db, file=file, uploader_id=current_user.id)

@router.get("/", response_model=List[Document])
def read_documents(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
) -> List[Document]:
    """
    获取文档列表
    """
    return get_documents(db, skip=skip, limit=limit, uploader_id=current_user.id)

@router.get("/{document_id}", response_model=Document)
def read_document(
    *,
    db: Session = Depends(get_db),
    document_id: int,
    current_user: User = Depends(get_current_user)
) -> Document:
    """
    获取单个文档
    """
    document = get_document(db, document_id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )
    if document.uploader_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限访问此文档"
        )
    return document

@router.put("/{document_id}", response_model=Document)
def update_document_endpoint(
    *,
    db: Session = Depends(get_db),
    document_id: int,
    document_in: DocumentUpdate,
    current_user: User = Depends(get_current_user)
) -> Document:
    """
    更新文档状态
    """
    document = get_document(db, document_id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )
    if document.uploader_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限修改此文档"
        )
    return update_document(db=db, document_id=document_id, document_in=document_in)

@router.delete("/{document_id}", response_model=Document)
def delete_document_endpoint(
    *,
    db: Session = Depends(get_db),
    document_id: int,
    current_user: User = Depends(get_current_user)
) -> Document:
    """
    删除文档
    """
    document = get_document(db, document_id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )
    if document.uploader_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限删除此文档"
        )
    return delete_document(db=db, document_id=document_id)