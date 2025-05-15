from typing import Optional, List, Any, Dict
from sqlalchemy.orm import Session
from app.models.annotation_review import AnnotationReview
from app.models.annotation import Annotation, AnnotationStatus
from app.schemas.annotation import AnnotationReviewCreate, AnnotationReviewUpdate
from fastapi import HTTPException

def get_annotation_review(db: Session, review_id: int) -> Optional[AnnotationReview]:
    """获取单个审核记录"""
    return db.query(AnnotationReview).filter(AnnotationReview.id == review_id).first()

def get_annotation_reviews(
    db: Session,
    *,
    annotation_id: Optional[int] = None,
    reviewer_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> List[AnnotationReview]:
    """获取审核记录列表，可按标注ID或审核人ID筛选"""
    query = db.query(AnnotationReview)
    if annotation_id is not None:
        query = query.filter(AnnotationReview.annotation_id == annotation_id)
    if reviewer_id is not None:
        query = query.filter(AnnotationReview.reviewer_id == reviewer_id)
    # 添加按创建时间降序排序，使最新的审核记录排在前面
    return query.order_by(AnnotationReview.created_at.desc()).offset(skip).limit(limit).all()

def create_annotation_review(
    db: Session,
    *,
    review_in: AnnotationReviewCreate
) -> AnnotationReview:
    """创建审核记录"""
    # 检查标注是否存在
    annotation = db.query(Annotation).filter(Annotation.id == review_in.annotation_id).first()
    if not annotation:
        raise HTTPException(status_code=404, detail="标注不存在")
    
    # 创建审核记录
    review_data = review_in.model_dump()
    db_review = AnnotationReview(**review_data)
    db.add(db_review)
    
    # 更新标注状态
    annotation.status = review_in.status
    annotation.reviewer_id = review_in.reviewer_id
    
    # 提交事务
    db.commit()
    db.refresh(db_review)
    return db_review

def update_annotation_review(
    db: Session,
    *,
    review_id: int,
    review_in: AnnotationReviewUpdate
) -> Optional[AnnotationReview]:
    """更新审核记录"""
    db_review = get_annotation_review(db, review_id)
    if not db_review:
        return None
    
    # 更新审核记录
    update_data = review_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_review, field, value)
    
    # 如果更新了状态，同时更新标注的状态
    if "status" in update_data:
        # 使用当前会话查询标注，避免DetachedInstanceError
        annotation_id = db_review.annotation_id
        annotation = db.query(Annotation).filter(Annotation.id == annotation_id).first()
        if annotation:
            annotation.status = update_data["status"]
    
    db.commit()
    db.refresh(db_review)
    return db_review

def delete_annotation_review(
    db: Session,
    *,
    review_id: int
) -> Optional[AnnotationReview]:
    """删除审核记录"""
    db_review = get_annotation_review(db, review_id)
    if not db_review:
        return None
    
    db.delete(db_review)
    db.commit()
    return db_review 