from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.annotation import (
    AnnotationCreate, Annotation, AnnotationUpdate, 
    AnnotationBatchCreate, AnnotationReviewCreate,
    AnnotationReview, AnnotationReviewUpdate
)
from app.schemas.annotation_history import AnnotationHistory
from app.services import annotation as annotation_service
from app.services import annotation_review as review_service

router = APIRouter()

@router.post("/", response_model=Annotation)
def create_annotation(
    annotation_in: AnnotationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建标注
    """
    return annotation_service.create_annotation(db=db, annotation_in=annotation_in)

@router.get("/", response_model=List[Annotation])
def get_annotations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    task_id: Optional[int] = None,
    annotator_id: Optional[int] = None,
    annotation_type: Optional[str] = None
):
    """
    获取标注列表
    """
    return annotation_service.get_annotations(
        db=db, 
        skip=skip, 
        limit=limit, 
        task_id=task_id, 
        annotator_id=annotator_id,
        annotation_type=annotation_type
    )

@router.get("/{annotation_id}", response_model=Annotation)
def get_annotation(
    annotation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取单个标注
    """
    annotation = annotation_service.get_annotation(db=db, annotation_id=annotation_id)
    if not annotation:
        raise HTTPException(
            status_code=404,
            detail="标注不存在"
        )
    return annotation

@router.put("/{annotation_id}", response_model=Annotation)
def update_annotation(
    annotation_id: int,
    annotation_in: AnnotationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新标注
    """
    annotation = annotation_service.get_annotation(db=db, annotation_id=annotation_id)
    if not annotation:
        raise HTTPException(
            status_code=404,
            detail="标注不存在"
        )
    
    # 确保当前用户有权限更新标注（管理员、标注创建者或者指定审核人）
    if not current_user.is_superuser and current_user.id != annotation.annotator_id and current_user.id != annotation.reviewer_id:
        raise HTTPException(
            status_code=403,
            detail="无权执行此操作"
        )
    
    return annotation_service.update_annotation(
        db=db, annotation_id=annotation_id, annotation_in=annotation_in
    )

@router.delete("/{annotation_id}", response_model=Annotation)
def delete_annotation(
    annotation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除标注
    """
    annotation = annotation_service.get_annotation(db=db, annotation_id=annotation_id)
    if not annotation:
        raise HTTPException(
            status_code=404,
            detail="标注不存在"
        )
    
    # 确保当前用户有权限删除标注（管理员或标注创建者）
    if not current_user.is_superuser and current_user.id != annotation.annotator_id:
        raise HTTPException(
            status_code=403,
            detail="无权执行此操作"
        )
    
    return annotation_service.delete_annotation(db=db, annotation_id=annotation_id)

@router.post("/batch", response_model=List[Annotation])
def create_annotations_batch(
    annotations_in: AnnotationBatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    批量创建标注
    """
    return annotation_service.create_annotations_batch(db=db, annotations_in=annotations_in)

@router.get("/{annotation_id}/history", response_model=List[AnnotationHistory])
def get_annotation_history(
    annotation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """
    获取标注历史记录
    """
    annotation = annotation_service.get_annotation(db=db, annotation_id=annotation_id)
    if not annotation:
        raise HTTPException(
            status_code=404,
            detail="标注不存在"
        )
    
    return annotation_service.get_annotation_history(
        db=db, annotation_id=annotation_id, skip=skip, limit=limit
    )

@router.post("/{annotation_id}/review", response_model=AnnotationReview)
def create_annotation_review(
    annotation_id: int,
    review_in: AnnotationReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建标注审核
    """
    # 确保当前用户有权限进行审核（管理员或指定的审核人员）
    if not current_user.is_superuser and current_user.id != review_in.reviewer_id:
        raise HTTPException(
            status_code=403,
            detail="无权执行此操作"
        )
    
    # 确保审核的是指定的标注
    if review_in.annotation_id != annotation_id:
        raise HTTPException(
            status_code=400,
            detail="标注ID不匹配"
        )
    
    # 创建审核记录
    return review_service.create_annotation_review(db=db, review_in=review_in)

@router.get("/{annotation_id}/reviews", response_model=List[AnnotationReview])
def get_annotation_reviews(
    annotation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """
    获取标注的审核历史
    """
    return review_service.get_annotation_reviews(
        db=db, annotation_id=annotation_id, skip=skip, limit=limit
    )

@router.get("/reviews/{review_id}", response_model=AnnotationReview)
def get_annotation_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取单个审核记录
    """
    review = review_service.get_annotation_review(db=db, review_id=review_id)
    if not review:
        raise HTTPException(
            status_code=404,
            detail="审核记录不存在"
        )
    return review

@router.put("/reviews/{review_id}", response_model=AnnotationReview)
def update_annotation_review(
    review_id: int,
    review_in: AnnotationReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新审核记录
    """
    review = review_service.get_annotation_review(db=db, review_id=review_id)
    if not review:
        raise HTTPException(
            status_code=404,
            detail="审核记录不存在"
        )
    
    # 确保当前用户有权限进行更新（管理员或原审核人）
    if not current_user.is_superuser and current_user.id != review.reviewer_id:
        raise HTTPException(
            status_code=403,
            detail="无权执行此操作"
        )
    
    return review_service.update_annotation_review(
        db=db, review_id=review_id, review_in=review_in
    )

@router.delete("/reviews/{review_id}", response_model=AnnotationReview)
def delete_annotation_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除审核记录（仅限管理员或原审核人）
    """
    review = review_service.get_annotation_review(db=db, review_id=review_id)
    if not review:
        raise HTTPException(
            status_code=404,
            detail="审核记录不存在"
        )
    
    # 确保当前用户有权限删除审核（管理员或原审核人）
    if not current_user.is_superuser and current_user.id != review.reviewer_id:
        raise HTTPException(
            status_code=403,
            detail="无权执行此操作"
        )
    
    return review_service.delete_annotation_review(db=db, review_id=review_id) 