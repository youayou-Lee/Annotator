from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.task import TaskStatus
from app.schemas.task import Task, TaskCreate, TaskUpdate
from app.services import task as task_service

router = APIRouter()

@router.post("/", response_model=Task)
def create_task(
    *,
    db: Session = Depends(get_db),
    task_in: TaskCreate,
    current_user: User = Depends(get_current_user)
) -> Task:
    """
    创建新任务
    """
    return task_service.create_task(db=db, task_in=task_in)

@router.get("/", response_model=List[Task])
def get_tasks(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    annotator_id: Optional[int] = None,
    reviewer_id: Optional[int] = None,
    status: Optional[TaskStatus] = None,
    current_user: User = Depends(get_current_user)
) -> List[Task]:
    """
    获取任务列表
    """
    return task_service.get_tasks(
        db=db,
        skip=skip,
        limit=limit,
        annotator_id=annotator_id,
        reviewer_id=reviewer_id,
        status=status
    )

@router.get("/{task_id}", response_model=Task)
def get_task(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    current_user: User = Depends(get_current_user)
) -> Task:
    """
    获取单个任务
    """
    db_task = task_service.get_task(db=db, task_id=task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return db_task

@router.put("/{task_id}", response_model=Task)
def update_task(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    task_in: TaskUpdate,
    current_user: User = Depends(get_current_user)
) -> Task:
    """
    更新任务
    """
    db_task = task_service.update_task(db=db, task_id=task_id, task_in=task_in)
    if not db_task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return db_task

@router.delete("/{task_id}", response_model=Task)
def delete_task(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    current_user: User = Depends(get_current_user)
) -> Task:
    """
    删除任务
    """
    db_task = task_service.delete_task(db=db, task_id=task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return db_task 