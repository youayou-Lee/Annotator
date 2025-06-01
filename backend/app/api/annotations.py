from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status

from ..models.user import UserInDB, UserRole
from ..models.annotation import (
    Annotation, AnnotationCreate, AnnotationUpdate, 
    AnnotationSubmit, AnnotationReview, AnnotationStatus
)
from ..core.security import get_current_user
from ..core.storage import StorageManager

router = APIRouter()
storage = StorageManager()


@router.get("/{task_id}/documents/{document_id}/annotation", response_model=Annotation, summary="获取标注数据")
async def get_annotation(
    task_id: str,
    document_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """获取标注数据"""
    # 检查任务权限
    task = storage.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    if current_user.role == UserRole.ANNOTATOR and task.assignee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此任务"
        )
    
    # 获取标注数据
    annotation = storage.get_annotation(task_id, document_id)
    if not annotation:
        # 如果不存在，创建新的标注记录
        annotation = Annotation(
            document_id=document_id,
            task_id=task_id,
            status=AnnotationStatus.PENDING,
            annotator_id=current_user.id,
            updated_at=datetime.now()
        )
        storage.save_annotation(annotation)
    
    return annotation


@router.post("/{task_id}/documents/{document_id}/annotation", response_model=Annotation, summary="保存标注数据")
async def save_annotation(
    task_id: str,
    document_id: str,
    annotation_update: AnnotationUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    """保存标注数据"""
    # 检查任务权限
    task = storage.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    if current_user.role == UserRole.ANNOTATOR and task.assignee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此任务"
        )
    
    # 获取或创建标注数据
    annotation = storage.get_annotation(task_id, document_id)
    if not annotation:
        annotation = Annotation(
            document_id=document_id,
            task_id=task_id,
            status=AnnotationStatus.IN_PROGRESS,
            annotator_id=current_user.id,
            updated_at=datetime.now()
        )
    
    # 更新标注数据
    if annotation_update.annotated_data is not None:
        annotation.annotated_data = annotation_update.annotated_data
    
    if annotation_update.status is not None:
        annotation.status = annotation_update.status
    
    annotation.updated_at = datetime.now()
    
    return storage.save_annotation(annotation)


@router.post("/{task_id}/documents/{document_id}/submit", response_model=Annotation, summary="提交标注")
async def submit_annotation(
    task_id: str,
    document_id: str,
    annotation_submit: AnnotationSubmit,
    current_user: UserInDB = Depends(get_current_user)
):
    """提交标注"""
    # 检查任务权限
    task = storage.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    if task.assignee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能提交分配给自己的任务"
        )
    
    # 获取或创建标注数据
    annotation = storage.get_annotation(task_id, document_id)
    if not annotation:
        annotation = Annotation(
            document_id=document_id,
            task_id=task_id,
            status=AnnotationStatus.COMPLETED,
            annotator_id=current_user.id,
            updated_at=datetime.now()
        )
    
    # 更新标注数据
    annotation.annotated_data = annotation_submit.annotated_data
    annotation.status = AnnotationStatus.COMPLETED
    annotation.updated_at = datetime.now()
    
    return storage.save_annotation(annotation)


@router.get("/{task_id}/documents/{document_id}/review", response_model=Annotation, summary="获取复审数据")
async def get_review(
    task_id: str,
    document_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """获取复审数据"""
    # 检查权限
    if current_user.role == UserRole.ANNOTATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="标注员无权进行复审"
        )
    
    annotation = storage.get_annotation(task_id, document_id)
    if not annotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标注数据不存在"
        )
    
    return annotation


@router.post("/{task_id}/documents/{document_id}/review", response_model=Annotation, summary="提交复审")
async def submit_review(
    task_id: str,
    document_id: str,
    review: AnnotationReview,
    current_user: UserInDB = Depends(get_current_user)
):
    """提交复审"""
    # 检查权限
    if current_user.role == UserRole.ANNOTATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="标注员无权进行复审"
        )
    
    annotation = storage.get_annotation(task_id, document_id)
    if not annotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标注数据不存在"
        )
    
    # 更新复审信息
    annotation.reviewer_id = current_user.id
    annotation.reviewed_at = datetime.now()
    annotation.status = AnnotationStatus.REVIEWED
    
    if review.revised_data:
        annotation.annotated_data = review.revised_data
    
    annotation.updated_at = datetime.now()
    
    return storage.save_annotation(annotation) 