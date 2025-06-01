from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from ..models.user import UserInDB, UserRole
from ..models.task import Task, TaskCreate, TaskUpdate
from ..core.security import get_current_user
from ..core.storage import StorageManager

router = APIRouter()
storage = StorageManager()


@router.get("/", response_model=List[Task], summary="获取任务列表")
async def get_tasks(current_user: UserInDB = Depends(get_current_user)):
    """获取任务列表"""
    tasks = storage.get_all_tasks()
    
    # 根据用户角色过滤任务
    if current_user.role == UserRole.ANNOTATOR:
        # 标注员只能看到分配给自己的任务
        tasks = [task for task in tasks if task.assignee_id == current_user.id]
    
    return tasks


@router.post("/", response_model=Task, summary="创建任务")
async def create_task(
    task_create: TaskCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    """创建任务"""
    # 检查权限
    if current_user.role == UserRole.ANNOTATOR:
        # 标注员只能创建分配给自己的任务
        if task_create.assignee_id and task_create.assignee_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="标注员只能创建分配给自己的任务"
            )
        task_create.assignee_id = current_user.id
    
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
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        if task.creator_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能删除自己创建的任务"
            )
    
    success = storage.delete_task(task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除任务失败"
        )
    
    return {"message": "任务删除成功"}


@router.post("/{task_id}/export", summary="导出任务数据")
async def export_task(task_id: str, current_user: UserInDB = Depends(get_current_user)):
    """导出任务数据"""
    return {"message": "导出功能待实现"} 