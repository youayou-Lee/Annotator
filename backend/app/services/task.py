from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate
from fastapi import HTTPException

def get_task(db: Session, task_id: int) -> Optional[Task]:
    return db.query(Task).filter(Task.id == task_id).first()

def get_tasks(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    annotator_id: Optional[int] = None,
    reviewer_id: Optional[int] = None,
    status: Optional[TaskStatus] = None
) -> List[Task]:
    query = db.query(Task)
    if annotator_id is not None:
        query = query.filter(Task.annotator_id == annotator_id)
    if reviewer_id is not None:
        query = query.filter(Task.reviewer_id == reviewer_id)
    if status is not None:
        query = query.filter(Task.status == status)
    return query.offset(skip).limit(limit).all()

def create_task(db: Session, *, task_in: TaskCreate) -> Task:
    db_task = Task(**task_in.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(
    db: Session,
    *,
    task_id: int,
    task_in: TaskUpdate
) -> Optional[Task]:
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    
    update_data = task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int) -> Optional[Task]:
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    
    db.delete(db_task)
    db.commit()
    return db_task 