from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.annotation import Annotation, AnnotationType
from app.schemas.annotation import AnnotationCreate, AnnotationUpdate
from fastapi import HTTPException

def get_annotation(db: Session, annotation_id: int) -> Optional[Annotation]:
    return db.query(Annotation).filter(Annotation.id == annotation_id).first()

def get_annotations(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    task_id: Optional[int] = None,
    annotator_id: Optional[int] = None,
    annotation_type: Optional[AnnotationType] = None
) -> List[Annotation]:
    query = db.query(Annotation)
    if task_id is not None:
        query = query.filter(Annotation.task_id == task_id)
    if annotator_id is not None:
        query = query.filter(Annotation.annotator_id == annotator_id)
    if annotation_type is not None:
        query = query.filter(Annotation.annotation_type == annotation_type)
    return query.offset(skip).limit(limit).all()

def create_annotation(db: Session, *, annotation_in: AnnotationCreate) -> Annotation:
    annotation_data = annotation_in.model_dump()
    db_annotation = Annotation(**annotation_data)
    db.add(db_annotation)
    db.commit()
    db.refresh(db_annotation)
    return db_annotation

def update_annotation(
    db: Session,
    *,
    annotation_id: int,
    annotation_in: AnnotationUpdate
) -> Optional[Annotation]:
    db_annotation = get_annotation(db, annotation_id)
    if not db_annotation:
        return None
    
    update_data = annotation_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_annotation, field, value)
    
    db.commit()
    db.refresh(db_annotation)
    return db_annotation

def delete_annotation(db: Session, annotation_id: int) -> Optional[Annotation]:
    db_annotation = get_annotation(db, annotation_id)
    if not db_annotation:
        return None
    
    db.delete(db_annotation)
    db.commit()
    return db_annotation 