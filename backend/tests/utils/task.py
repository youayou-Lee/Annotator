from typing import Optional

from sqlalchemy.orm import Session

from app.services.task import create_task
from app.schemas.task import TaskCreate
from app.models.task import Task, TaskStatus
from tests.utils.utils import random_lower_string

def create_random_task(db: Session, document_id: int, annotator_id: int, user_id: int) -> Task:
    """创建一个随机任务"""
    title = random_lower_string()
    description = random_lower_string()
    task_in = TaskCreate(
        document_id=document_id,
        annotator_id=annotator_id,
        user_id=user_id,
        status=TaskStatus.PENDING,
        title=title,
        description=description
    )
    return create_task(db, task_in=task_in) 