import os
import uuid
import shutil
import json
import mimetypes
from typing import List, Optional
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Form
from fastapi.responses import FileResponse, StreamingResponse

from ..models.user import UserInDB, UserRole
from ..models.file import (
    FileInfo, FileUpload, FilePreview, FileType, FileListResponse,
    FileDeleteResponse, TemplateValidationResponse, BatchFileUpload,
    FileDownloadInfo
)
from ..core.security import get_current_user
from ..core.storage import StorageManager
from ..config import settings

router = APIRouter()
storage = StorageManager()


def check_file_permissions(current_user: UserInDB, file_info: FileInfo = None, operation: str = "read"):
    """检查文件操作权限"""
    if current_user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        return True
    
    if operation == "delete" and file_info:
        # 普通用户只能删除自己上传的文件
        return file_info.uploader_id == current_user.id
    
    if operation in ["upload", "read", "download"]:
        return True
    
    return False


@router.get("/", response_model=FileListResponse, summary="获取文件列表")
async def get_files(
    file_type: Optional[FileType] = Query(None, description="文件类型筛选"),
    current_user: UserInDB = Depends(get_current_user)
):
    """获取文件列表，支持按类型筛选"""
    try:
        files = storage.get_all_files(file_type)
        
        # 按上传时间倒序排列
        files.sort(key=lambda x: x.uploaded_at, reverse=True)
        
        return FileListResponse(
            files=files,
            total=len(files),
            file_type=file_type
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取文件列表失败: {str(e)}"
        )


@router.post("/upload", response_model=FileUpload, summary="上传文件")
async def upload_file(
    file: UploadFile = File(...),
    file_type: FileType = Form(..., description="文件类型"),
    current_user: UserInDB = Depends(get_current_user)
):
    """上传单个文件"""
    if not check_file_permissions(current_user, operation="upload"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有上传权限"
        )
    
    # 检查文件大小
    if file.size and file.size > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"文件大小超过限制 ({settings.max_file_size // (1024*1024)}MB)"
        )
    
    # 检查文件扩展名
    file_ext = Path(file.filename).suffix.lower()
    if file_type == FileType.DOCUMENT:
        allowed_exts = settings.allowed_document_extensions
    elif file_type == FileType.TEMPLATE:
        allowed_exts = settings.allowed_template_extensions
    else:
        allowed_exts = [".json", ".jsonl", ".py", ".txt", ".csv", ".xlsx"]
    
    if file_ext not in allowed_exts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型: {file_ext}，允许的类型: {', '.join(allowed_exts)}"
        )
    
    # 生成文件ID和路径
    file_id = f"file_{uuid.uuid4().hex[:8]}"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    
    # 确定保存路径
    if file_type == FileType.DOCUMENT:
        save_dir = Path(settings.data_dir) / "public_files" / "documents"
    elif file_type == FileType.TEMPLATE:
        save_dir = Path(settings.data_dir) / "public_files" / "templates"
    else:
        save_dir = Path(settings.data_dir) / "public_files" / "exports"
    
    save_dir.mkdir(parents=True, exist_ok=True)
    file_path = save_dir / safe_filename
    
    # 保存文件
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件保存失败: {str(e)}"
        )
    
    # 获取文件大小
    file_size = file_path.stat().st_size
    
    # 如果是模板文件，进行验证
    if file_type == FileType.TEMPLATE:
        relative_path = str(file_path.relative_to(Path(settings.data_dir)))
        validation_result = storage.validate_python_template(relative_path)
        if not validation_result["valid"]:
            # 删除无效文件
            file_path.unlink()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"模板文件验证失败: {validation_result['error']}"
            )
    
    # 保存文件信息到元数据
    relative_path = str(file_path.relative_to(Path(settings.data_dir)))
    file_info = FileInfo(
        id=file_id,
        filename=file.filename,
        file_path=relative_path,
        file_type=file_type,
        file_size=file_size,
        uploader_id=current_user.id,
        uploaded_at=datetime.now()
    )
    
    storage.save_file_info(file_info)
    
    return FileUpload(
        file_id=file_id,
        filename=file.filename,
        file_path=relative_path,
        file_size=file_size,
        file_type=file_type,
        message="文件上传成功"
    )


@router.post("/upload/batch", response_model=BatchFileUpload, summary="批量上传文件")
async def upload_files_batch(
    files: List[UploadFile] = File(...),
    file_type: FileType = Form(..., description="文件类型"),
    current_user: UserInDB = Depends(get_current_user)
):
    """批量上传文件"""
    if not check_file_permissions(current_user, operation="upload"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有上传权限"
        )
    
    successful_uploads = []
    failed_uploads = []
    
    for file in files:
        try:
            # 重用单文件上传逻辑
            result = await upload_file(file, file_type, current_user)
            successful_uploads.append(result)
        except HTTPException as e:
            failed_uploads.append({
                "filename": file.filename,
                "error": e.detail
            })
        except Exception as e:
            failed_uploads.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return BatchFileUpload(
        successful_uploads=successful_uploads,
        failed_uploads=failed_uploads,
        total_uploaded=len(successful_uploads),
        total_failed=len(failed_uploads)
    )


@router.delete("/{file_id}", response_model=FileDeleteResponse, summary="删除文件")
async def delete_file(
    file_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """删除文件"""
    # 获取文件信息
    file_info = storage.get_file_by_id(file_id)
    if not file_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    # 检查权限
    if not check_file_permissions(current_user, file_info, "delete"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有删除权限"
        )
    
    try:
        # 删除物理文件
        if storage.delete_physical_file(file_info.file_path):
            # 删除元数据
            storage.delete_file_info(file_id)
            return FileDeleteResponse(
                success=True,
                message="文件删除成功",
                file_id=file_id
            )
        else:
            return FileDeleteResponse(
                success=False,
                message="文件删除失败：物理文件不存在",
                file_id=file_id
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除文件失败: {str(e)}"
        )


@router.get("/{file_id}/download", summary="下载文件")
async def download_file(
    file_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """下载文件"""
    if not check_file_permissions(current_user, operation="download"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有下载权限"
        )
    
    # 获取文件信息
    file_info = storage.get_file_by_id(file_id)
    if not file_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    # 构建文件路径
    file_path = Path(settings.data_dir) / file_info.file_path
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    # 确定MIME类型
    content_type, _ = mimetypes.guess_type(str(file_path))
    if content_type is None:
        content_type = "application/octet-stream"
    
    return FileResponse(
        path=str(file_path),
        filename=file_info.filename,
        media_type=content_type
    )


@router.get("/download/batch", summary="批量下载文件")
async def download_files_batch(
    file_ids: str = Query(..., description="文件ID列表，逗号分隔"),
    current_user: UserInDB = Depends(get_current_user)
):
    """批量下载文件（返回ZIP压缩包）"""
    if not check_file_permissions(current_user, operation="download"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有下载权限"
        )
    
    import zipfile
    import io
    
    file_id_list = [fid.strip() for fid in file_ids.split(",")]
    
    # 创建内存中的ZIP文件
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_id in file_id_list:
            file_info = storage.get_file_by_id(file_id)
            if file_info:
                file_path = Path(settings.data_dir) / file_info.file_path
                if file_path.exists():
                    zip_file.write(file_path, file_info.filename)
    
    zip_buffer.seek(0)
    
    return StreamingResponse(
        io.BytesIO(zip_buffer.read()),
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=files.zip"}
    )


@router.get("/{file_id}/preview", response_model=FilePreview, summary="预览文件")
async def preview_file(
    file_id: str,
    max_size: int = Query(1024*1024, description="最大预览大小（字节）"),
    current_user: UserInDB = Depends(get_current_user)
):
    """预览文件内容"""
    if not check_file_permissions(current_user, operation="read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有预览权限"
        )
    
    # 获取文件信息
    file_info = storage.get_file_by_id(file_id)
    if not file_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    # 检查文件大小
    if file_info.file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"文件过大，无法预览（最大{max_size//1024}KB）"
        )
    
    # 读取文件内容
    content = storage.get_file_content(file_info.file_path)
    if content is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="无法读取文件内容"
        )
    
    # 确定文件类型
    file_ext = Path(file_info.filename).suffix.lower()
    if file_ext in [".json", ".jsonl"]:
        file_type = "json"
        # 尝试格式化JSON
        try:
            if file_ext == ".json":
                parsed = json.loads(content)
                content = json.dumps(parsed, ensure_ascii=False, indent=2)
            else:  # jsonl
                lines = content.strip().split('\n')
                formatted_lines = []
                for line in lines:
                    if line.strip():
                        parsed = json.loads(line)
                        formatted_lines.append(json.dumps(parsed, ensure_ascii=False))
                content = '\n'.join(formatted_lines)
        except json.JSONDecodeError:
            pass  # 保持原始内容
    elif file_ext == ".py":
        file_type = "python"
    else:
        file_type = "text"
    
    return FilePreview(
        filename=file_info.filename,
        content=content,
        file_type=file_type,
        file_size=file_info.file_size
    )


@router.get("/{file_id}/validate", response_model=TemplateValidationResponse, summary="验证模板文件")
async def validate_template(
    file_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """验证Python模板文件"""
    # 获取文件信息
    file_info = storage.get_file_by_id(file_id)
    if not file_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    if file_info.file_type != FileType.TEMPLATE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能验证模板文件"
        )
    
    # 验证模板
    validation_result = storage.validate_python_template(file_info.file_path)
    
    return TemplateValidationResponse(**validation_result)


@router.get("/my-files", response_model=FileListResponse, summary="获取我的文件")
async def get_my_files(
    file_type: Optional[FileType] = Query(None, description="文件类型筛选"),
    current_user: UserInDB = Depends(get_current_user)
):
    """获取当前用户上传的文件"""
    try:
        my_files = storage.get_files_by_uploader(current_user.id)
        
        # 按类型筛选
        if file_type:
            my_files = [f for f in my_files if f.file_type == file_type]
        
        # 按上传时间倒序排列
        my_files.sort(key=lambda x: x.uploaded_at, reverse=True)
        
        return FileListResponse(
            files=my_files,
            total=len(my_files),
            file_type=file_type
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取文件列表失败: {str(e)}"
        ) 