from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.annotation import AnnotationType
from app.schemas.annotation import Annotation, AnnotationCreate, AnnotationUpdate
from app.services import annotation as annotation_service

router = APIRouter()

@router.post("/", response_model=Annotation)
def create_annotation(
    *,
    db: Session = Depends(get_db),
    annotation_in: AnnotationCreate,
    current_user: User = Depends(get_current_user)
) -> Annotation:
    """
    创建新标注
    """
    return annotation_service.create_annotation(db=db, annotation_in=annotation_in)

@router.get("/", response_model=List[Annotation])
def get_annotations(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    task_id: Optional[int] = None,
    annotator_id: Optional[int] = None,
    annotation_type: Optional[AnnotationType] = None,
    current_user: User = Depends(get_current_user)
) -> List[Annotation]:
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
    *,
    db: Session = Depends(get_db),
    annotation_id: int,
    current_user: User = Depends(get_current_user)
) -> Annotation:
    """
    获取单个标注
    """
    db_annotation = annotation_service.get_annotation(db=db, annotation_id=annotation_id)
    if not db_annotation:
        raise HTTPException(status_code=404, detail="标注不存在")
    return db_annotation

@router.put("/{annotation_id}", response_model=Annotation)
def update_annotation(
    *,
    db: Session = Depends(get_db),
    annotation_id: int,
    annotation_in: AnnotationUpdate,
    current_user: User = Depends(get_current_user)
) -> Annotation:
    """
    更新标注
    """
    db_annotation = annotation_service.update_annotation(
        db=db,
        annotation_id=annotation_id,
        annotation_in=annotation_in
    )
    if not db_annotation:
        raise HTTPException(status_code=404, detail="标注不存在")
    return db_annotation

@router.delete("/{annotation_id}", response_model=Annotation)
def delete_annotation(
    *,
    db: Session = Depends(get_db),
    annotation_id: int,
    current_user: User = Depends(get_current_user)
) -> Annotation:
    """
    删除标注
    """
    db_annotation = annotation_service.delete_annotation(db=db, annotation_id=annotation_id)
    if not db_annotation:
        raise HTTPException(status_code=404, detail="标注不存在")
    return db_annotation 