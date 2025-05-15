from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.export_task import ExportStatus
from app.schemas.export_task import ExportTask, ExportTaskCreate, ExportTaskUpdate
from app.services import export as export_service
import os

router = APIRouter()

@router.post("/", response_model=ExportTask)
def create_export_task(
    *,
    export_task_in: ExportTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建导出任务
    """
    # 确保当前用户有权限创建导出任务（必须是自己的数据）
    if not current_user.is_superuser and current_user.id != export_task_in.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权执行此操作"
        )
    
    return export_service.create_export_task(db=db, export_task_in=export_task_in)

@router.get("/", response_model=List[ExportTask])
def get_export_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    status: Optional[ExportStatus] = None
):
    """
    获取导出任务列表
    
    参数:
    - skip: 跳过记录数
    - limit: 查询记录数上限
    - status: 筛选状态
    """
    # 管理员可以查看所有任务，普通用户只能查看自己的任务
    if current_user.is_superuser:
        return export_service.get_export_tasks(
            db=db, skip=skip, limit=limit, status=status
        )
    else:
        return export_service.get_export_tasks(
            db=db, user_id=current_user.id, skip=skip, limit=limit, status=status
        )

@router.get("/{export_task_id}", response_model=ExportTask)
def get_export_task(
    export_task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取单个导出任务详情
    """
    db_export_task = export_service.get_export_task(db=db, export_task_id=export_task_id)
    if not db_export_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="导出任务不存在"
        )
    
    # 检查权限：只有管理员或者任务的创建者可以查看任务
    if not current_user.is_superuser and current_user.id != db_export_task.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权执行此操作"
        )
    
    return db_export_task

@router.get("/{export_task_id}/download")
def download_export_file(
    export_task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    下载导出文件
    """
    db_export_task = export_service.get_export_task(db=db, export_task_id=export_task_id)
    if not db_export_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="导出任务不存在"
        )
    
    # 检查权限：只有管理员或者任务的创建者可以下载文件
    if not current_user.is_superuser and current_user.id != db_export_task.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权执行此操作"
        )
    
    # 检查任务是否已完成
    if db_export_task.status != ExportStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"导出任务尚未完成，当前状态: {db_export_task.status}"
        )
    
    # 检查文件是否存在
    if not db_export_task.file_path or not os.path.exists(db_export_task.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="导出文件不存在"
        )
    
    # 返回文件
    return FileResponse(
        path=db_export_task.file_path,
        filename=os.path.basename(db_export_task.file_path),
        media_type="application/octet-stream"
    )

@router.delete("/{export_task_id}", response_model=ExportTask)
def delete_export_task(
    export_task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除导出任务
    """
    db_export_task = export_service.get_export_task(db=db, export_task_id=export_task_id)
    if not db_export_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="导出任务不存在"
        )
    
    # 检查权限：只有管理员或者任务的创建者可以删除任务
    if not current_user.is_superuser and current_user.id != db_export_task.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权执行此操作"
        )
    
    return export_service.delete_export_task(db=db, export_task_id=export_task_id) 