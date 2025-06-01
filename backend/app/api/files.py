import os
import uuid
import shutil
from typing import List, Optional
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import FileResponse

from ..models.user import UserInDB
from ..models.file import FileInfo, FileUpload, FilePreview, FileType
from ..core.security import get_current_user
from ..core.storage import StorageManager
from ..config import settings

router = APIRouter()
storage = StorageManager()


@router.get("/", summary="获取文件列表")
async def get_files(
    file_type: Optional[FileType] = Query(None, description="文件类型"),
    current_user: UserInDB = Depends(get_current_user)
):
    """获取文件列表"""
    # 这里返回空列表，实际实现需要扩展存储管理器
    return {"files": [], "message": "文件列表功能待实现"}


@router.post("/upload", response_model=FileUpload, summary="上传文件")
async def upload_file(
    file: UploadFile = File(...),
    file_type: FileType = Query(..., description="文件类型"),
    current_user: UserInDB = Depends(get_current_user)
):
    """上传文件"""
    # 检查文件大小
    if file.size and file.size > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"文件大小超过限制 ({settings.max_file_size} bytes)"
        )
    
    # 检查文件扩展名
    file_ext = Path(file.filename).suffix.lower()
    if file_type == FileType.DOCUMENT:
        allowed_exts = settings.allowed_document_extensions
    elif file_type == FileType.TEMPLATE:
        allowed_exts = settings.allowed_template_extensions
    else:
        allowed_exts = [".json", ".jsonl", ".py", ".txt"]
    
    if file_ext not in allowed_exts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型: {file_ext}"
        )
    
    # 生成文件ID和路径
    file_id = f"file_{uuid.uuid4().hex[:8]}"
    filename = f"{file_id}_{file.filename}"
    
    # 确定保存路径
    if file_type == FileType.DOCUMENT:
        save_dir = Path(settings.data_dir) / "public_files" / "documents"
    elif file_type == FileType.TEMPLATE:
        save_dir = Path(settings.data_dir) / "public_files" / "templates"
    else:
        save_dir = Path(settings.data_dir) / "uploads"
    
    save_dir.mkdir(parents=True, exist_ok=True)
    file_path = save_dir / filename
    
    # 保存文件
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件保存失败: {str(e)}"
        )
    
    # 返回文件信息
    relative_path = str(file_path.relative_to(Path(settings.data_dir)))
    
    return FileUpload(
        file_id=file_id,
        filename=file.filename,
        file_path=relative_path,
        message="文件上传成功"
    )


@router.delete("/{file_id}", summary="删除文件")
async def delete_file(
    file_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """删除文件"""
    # 这里返回成功消息，实际实现需要扩展存储管理器
    return {"message": f"文件 {file_id} 删除功能待实现"}


@router.get("/{file_id}/download", summary="下载文件")
async def download_file(
    file_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """下载文件"""
    # 这里返回错误，实际实现需要扩展存储管理器
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="文件下载功能待实现"
    )


@router.get("/{file_id}/preview", response_model=FilePreview, summary="预览文件")
async def preview_file(
    file_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """预览文件内容"""
    # 这里返回空内容，实际实现需要扩展存储管理器
    return FilePreview(
        filename="unknown",
        content="文件预览功能待实现",
        file_type="text"
    ) 