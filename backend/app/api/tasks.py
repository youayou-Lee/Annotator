from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

from ..models.user import UserInDB, UserRole
from ..models.task import (
    Task, TaskCreate, TaskUpdate, TaskQuery, TaskListResponse, 
    TaskStatistics, TaskStatus, DocumentStatus
)
from ..models.file import FileType
from ..core.security import get_current_user
from ..core.storage import StorageManager

router = APIRouter()
storage = StorageManager()


@router.get("/", response_model=TaskListResponse, summary="获取任务列表")
async def get_tasks(
    status: Optional[TaskStatus] = Query(None, description="任务状态筛选"),
    assignee_id: Optional[str] = Query(None, description="分配人ID筛选"),
    creator_id: Optional[str] = Query(None, description="创建人ID筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    current_user: UserInDB = Depends(get_current_user)
):
    """获取任务列表，支持筛选、分页和搜索"""
    
    # 构建查询参数
    query = TaskQuery(
        status=status,
        assignee_id=assignee_id,
        creator_id=creator_id,
        page=page,
        page_size=page_size,
        search=search
    )
    
    # 根据用户角色调整查询条件
    if current_user.role == UserRole.ANNOTATOR:
        # 标注员只能看到分配给自己的任务
        query.assignee_id = current_user.id
    
    return storage.get_tasks_with_query(query)


@router.get("/statistics", response_model=TaskStatistics, summary="获取任务统计")
async def get_task_statistics(current_user: UserInDB = Depends(get_current_user)):
    """获取任务统计信息"""
    return storage.get_task_statistics(current_user.id)


@router.post("/", response_model=Task, summary="创建任务")
async def create_task(
    task_create: TaskCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    """创建任务"""
    
    # 验证文档文件是否存在
    if not task_create.documents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="至少需要选择一个文档文件"
        )
    
    # 验证文档文件
    document_files = storage.get_all_files(FileType.DOCUMENT)
    valid_doc_paths = {f.file_path for f in document_files}
    
    for doc_path in task_create.documents:
        if doc_path not in valid_doc_paths:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文档文件不存在: {doc_path}"
            )
    
    # 验证模板文件
    if task_create.template_path:
        template_files = storage.get_all_files(FileType.TEMPLATE)
        valid_template_paths = {f.file_path for f in template_files}
        
        if task_create.template_path not in valid_template_paths:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"模板文件不存在: {task_create.template_path}"
            )
        
        # 验证模板文件格式
        validation_result = storage.validate_python_template(task_create.template_path)
        if not validation_result.get("valid"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"模板文件格式错误: {validation_result.get('error', '未知错误')}"
            )
    
    # 检查权限
    if current_user.role == UserRole.ANNOTATOR:
        # 标注员只能创建分配给自己的任务
        if task_create.assignee_id and task_create.assignee_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="标注员只能创建分配给自己的任务"
            )
        task_create.assignee_id = current_user.id
    
    # 验证分配人是否存在
    if task_create.assignee_id:
        assignee = storage.get_user_by_id(task_create.assignee_id)
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="指定的分配人不存在"
            )
    
    return storage.create_task(task_create, current_user.id)


@router.get("/{task_id}", response_model=Task, summary="获取任务详情")
async def get_task(task_id: str, current_user: UserInDB = Depends(get_current_user)):
    """获取任务详情"""
    task = storage.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查权限
    if current_user.role == UserRole.ANNOTATOR:
        if task.assignee_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此任务"
            )
    
    return task


@router.put("/{task_id}", response_model=Task, summary="更新任务")
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    """更新任务"""
    task = storage.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查权限
    if current_user.role == UserRole.ANNOTATOR:
        if task.assignee_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权修改此任务"
            )
        # 标注员不能修改分配人
        if task_update.assignee_id is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="标注员无权修改任务分配"
            )
    
    # 验证分配人是否存在
    if task_update.assignee_id:
        assignee = storage.get_user_by_id(task_update.assignee_id)
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="指定的分配人不存在"
            )
    
    update_data = task_update.dict(exclude_unset=True)
    updated_task = storage.update_task(task_id, update_data)
    
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新任务失败"
        )
    
    return updated_task


@router.delete("/{task_id}", summary="删除任务")
async def delete_task(task_id: str, current_user: UserInDB = Depends(get_current_user)):
    """删除任务"""
    task = storage.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查权限
    if current_user.role == UserRole.ANNOTATOR:
        # 标注员只能删除自己创建的任务
        if task.creator_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能删除自己创建的任务"
            )
    elif current_user.role == UserRole.ADMIN:
        # 管理员可以删除所有任务，但不能删除超级管理员创建的任务
        if task.creator_id != current_user.id:
            creator = storage.get_user_by_id(task.creator_id)
            if creator and creator.role == UserRole.SUPER_ADMIN:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权删除超级管理员创建的任务"
                )
    # 超级管理员可以删除所有任务
    
    success = storage.delete_task(task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除任务失败"
        )
    
    return {"message": "任务删除成功"}


@router.put("/{task_id}/documents/{document_id}/status", response_model=Task, summary="更新文档状态")
async def update_document_status(
    task_id: str,
    document_id: str,
    status: DocumentStatus,
    current_user: UserInDB = Depends(get_current_user)
):
    """更新文档状态"""
    task = storage.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查权限
    if current_user.role == UserRole.ANNOTATOR:
        if task.assignee_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权修改此任务的文档状态"
            )
    
    # 检查文档是否存在
    document_exists = any(doc.id == document_id for doc in task.documents)
    if not document_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )
    
    updated_task = storage.update_document_status(task_id, document_id, status)
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新文档状态失败"
        )
    
    return updated_task


@router.get("/{task_id}/progress", response_model=dict, summary="获取任务进度详情")
async def get_task_progress(task_id: str, current_user: UserInDB = Depends(get_current_user)):
    """获取任务进度详情"""
    task = storage.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查权限
    if current_user.role == UserRole.ANNOTATOR:
        if task.assignee_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此任务"
            )
    
    return {
        "task_id": task.id,
        "task_name": task.name,
        "status": task.status,
        "progress": task.progress.dict() if task.progress else None,
        "documents": [
            {
                "id": doc.id,
                "filename": doc.filename,
                "status": doc.status,
                "file_size": doc.file_size
            }
            for doc in task.documents
        ]
    }


@router.post("/{task_id}/export", summary="导出任务数据")
async def export_task(task_id: str, current_user: UserInDB = Depends(get_current_user)):
    """导出任务数据"""
    task = storage.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查权限
    if current_user.role == UserRole.ANNOTATOR:
        if task.assignee_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权导出此任务"
            )
    
    # TODO: 实现具体的导出逻辑
    return {"message": "导出功能待实现", "task_id": task_id}


@router.get("/{task_id}/template/fields", summary="获取任务模板字段")
async def get_task_template_fields(task_id: str, current_user: UserInDB = Depends(get_current_user)):
    """获取任务模板字段信息"""
    task = storage.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查权限
    if current_user.role == UserRole.ANNOTATOR:
        if task.assignee_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此任务"
            )
    
    if not task.template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务未配置模板"
        )
    
    return {
        "template_filename": task.template.filename,
        "fields": task.template.fields or {},
        "validation_result": task.template.validation_result or {}
    } 