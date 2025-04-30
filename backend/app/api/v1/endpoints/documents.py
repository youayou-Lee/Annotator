from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentResponse
from app.services.document import DocumentService

router = APIRouter()

@router.post("/", response_model=DocumentResponse)
def create_document(
    document: DocumentCreate,
    db: Session = Depends(get_db)
):
    """创建新文档"""
    return DocumentService.create_document(db=db, document=document)

@router.get("/", response_model=List[DocumentResponse])
def get_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取文档列表"""
    return DocumentService.get_documents(db=db, skip=skip, limit=limit)

@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """获取单个文档"""
    document = DocumentService.get_document(db=db, document_id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """上传文档文件"""
    return await DocumentService.upload_document(db=db, file=file)

@router.put("/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: int,
    document: DocumentCreate,
    db: Session = Depends(get_db)
):
    """更新文档"""
    updated_document = DocumentService.update_document(
        db=db,
        document_id=document_id,
        document=document
    )
    if not updated_document:
        raise HTTPException(status_code=404, detail="Document not found")
    return updated_document

@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """删除文档"""
    success = DocumentService.delete_document(db=db, document_id=document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document deleted successfully"} 