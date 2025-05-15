from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from app.models.annotation import Annotation, AnnotationType, AnnotationStatus
from app.models.annotation_history import AnnotationHistory
from app.schemas.annotation import AnnotationCreate, AnnotationUpdate, AnnotationBatchCreate
from app.schemas.annotation_history import AnnotationHistoryCreate
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

def create_annotation_history(
    db: Session,
    *,
    annotation_id: int,
    user_id: int,
    action: str,
    content: dict
) -> AnnotationHistory:
    """
    创建标注历史记录
    """
    history_in = AnnotationHistoryCreate(
        annotation_id=annotation_id,
        user_id=user_id,
        action=action,
        content=content
    )
    history_data = history_in.model_dump()
    db_history = AnnotationHistory(**history_data)
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history

def check_text_overlap(content1: dict, content2: dict) -> bool:
    """
    检查两个文本标注是否重叠
    """
    if not all(k in content1 for k in ["start_offset", "end_offset"]) or \
       not all(k in content2 for k in ["start_offset", "end_offset"]):
        return False
    
    start1, end1 = content1["start_offset"], content1["end_offset"]
    start2, end2 = content2["start_offset"], content2["end_offset"]
    
    return not (end1 <= start2 or end2 <= start1)

def check_annotation_conflict(
    db: Session,
    *,
    annotation: Annotation,
    task_id: int
) -> Tuple[bool, Optional[Annotation]]:
    """
    检查标注是否存在冲突
    返回: (是否存在冲突, 冲突的标注)
    """
    # 获取同一任务下的所有标注
    existing_annotations = db.query(Annotation).filter(
        Annotation.task_id == task_id,
        Annotation.id != annotation.id,
        Annotation.status != AnnotationStatus.REJECTED
    ).all()
    
    for existing in existing_annotations:
        # 检查标注类型是否相同
        if existing.annotation_type != annotation.annotation_type:
            continue
            
        # 根据标注类型检查冲突
        if annotation.annotation_type == AnnotationType.TEXT:
            if check_text_overlap(annotation.content, existing.content):
                return True, existing
                
        # TODO: 添加其他类型标注的冲突检测逻辑
        
    return False, None

def create_annotation(db: Session, *, annotation_in: AnnotationCreate) -> Annotation:
    annotation_data = annotation_in.model_dump()
    db_annotation = Annotation(**annotation_data)
    
    # 先添加并提交新标注，确保其有ID
    db.add(db_annotation)
    db.commit()
    db.refresh(db_annotation)
    
    # 检查冲突
    has_conflict, conflicting_annotation = check_annotation_conflict(
        db=db,
        annotation=db_annotation,
        task_id=annotation_in.task_id
    )
    
    # 如果有冲突，更新冲突状态
    if has_conflict:
        db_annotation.status = AnnotationStatus.CONFLICT
        db_annotation.conflict_with = conflicting_annotation.id
        
        # 更新冲突标注的状态
        conflicting_annotation.status = AnnotationStatus.CONFLICT
        conflicting_annotation.conflict_with = db_annotation.id
        
        # 提交更新
        db.commit()
        db.refresh(db_annotation)
    
    # 创建历史记录
    create_annotation_history(
        db=db,
        annotation_id=db_annotation.id,
        user_id=db_annotation.annotator_id,
        action="CREATE",
        content=annotation_data
    )
    
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
    
    # 保存更新前的数据
    old_content = db_annotation.content
    
    update_data = annotation_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_annotation, field, value)
    
    # 如果更新了content，重新检查冲突
    if "content" in update_data:
        has_conflict, conflicting_annotation = check_annotation_conflict(
            db=db,
            annotation=db_annotation,
            task_id=db_annotation.task_id
        )
        
        if has_conflict:
            db_annotation.status = AnnotationStatus.CONFLICT
            db_annotation.conflict_with = conflicting_annotation.id
            
            # 先提交当前标注的更改
            db.commit()
            db.refresh(db_annotation)
            
            # 更新冲突标注的状态
            conflicting_annotation.status = AnnotationStatus.CONFLICT
            conflicting_annotation.conflict_with = db_annotation.id
            
            # 再次提交以更新冲突标注
            db.commit()
            db.refresh(db_annotation)
        else:
            # 如果没有冲突，正常提交
            db.commit()
            db.refresh(db_annotation)
    else:
        # 如果没有更新content，正常提交
        db.commit()
        db.refresh(db_annotation)
    
    # 创建历史记录
    create_annotation_history(
        db=db,
        annotation_id=db_annotation.id,
        user_id=db_annotation.annotator_id,
        action="UPDATE",
        content={
            "old_content": old_content,
            "new_content": db_annotation.content
        }
    )
    
    return db_annotation

def delete_annotation(db: Session, annotation_id: int) -> Annotation:
    """
    删除标注
    """
    annotation = db.query(Annotation).filter(Annotation.id == annotation_id).first()
    if not annotation:
        raise HTTPException(status_code=404, detail="标注不存在")
    
    # 保存标注内容以创建历史记录
    annotation_content = {
        "annotation_type": annotation.annotation_type.value,
        "content": annotation.content,
        "status": annotation.status.value,
        "created_at": annotation.created_at.isoformat(),
        "updated_at": annotation.updated_at.isoformat(),
    }
    
    # 创建一个删除历史记录
    history_data = {
        "annotation_id": annotation_id,  # 保持原始annotation_id
        "user_id": annotation.annotator_id,  # 使用标注者作为删除操作的执行者
        "action": "DELETE",
        "content": annotation_content
    }
    db_history = AnnotationHistory(**history_data)
    db.add(db_history)
    
    # 删除标注
    db.delete(annotation)
    db.commit()
    
    # 返回已删除的标注对象
    return annotation

def create_annotations_batch(db: Session, *, annotations_in: AnnotationBatchCreate) -> List[Annotation]:
    """
    批量创建标注
    """
    db_annotations = []
    for annotation_in in annotations_in.annotations:
        annotation_data = annotation_in.model_dump()
        db_annotation = Annotation(**annotation_data)
        db.add(db_annotation)
        db_annotations.append(db_annotation)
    
    try:
        db.commit()
        for annotation in db_annotations:
            db.refresh(annotation)
        return db_annotations
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"批量创建标注失败: {str(e)}")

def get_annotation_history(
    db: Session,
    *,
    annotation_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[AnnotationHistory]:
    """
    获取标注的历史记录
    """
    return db.query(AnnotationHistory).filter(
        AnnotationHistory.annotation_id == annotation_id
    ).order_by(AnnotationHistory.created_at.desc()).offset(skip).limit(limit).all() 