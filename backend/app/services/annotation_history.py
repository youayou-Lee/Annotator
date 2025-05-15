from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.annotation_history import AnnotationHistory
from app.models.annotation import Annotation
from app.schemas.annotation_history import AnnotationHistoryCreate
from datetime import datetime

def create_annotation_history(
    db: Session,
    *,
    annotation_id: int,
    user_id: int,
    action: str,
    content: Dict[str, Any]
) -> AnnotationHistory:
    """
    创建标注历史记录
    action: "CREATE", "UPDATE", "DELETE"
    """
    history_data = {
        "annotation_id": annotation_id,
        "user_id": user_id,
        "action": action,
        "content": content
    }
    history = AnnotationHistory(**history_data)
    db.add(history)
    db.commit()
    db.refresh(history)
    return history

def get_annotation_history(
    db: Session,
    *,
    annotation_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[AnnotationHistory]:
    """
    获取指定标注的历史记录
    """
    return db.query(AnnotationHistory)\
        .filter(AnnotationHistory.annotation_id == annotation_id)\
        .order_by(AnnotationHistory.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_user_history(
    db: Session,
    *,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    action: Optional[str] = None,
    order: str = "desc"
) -> List[AnnotationHistory]:
    """
    获取指定用户的所有操作历史
    
    参数:
    - user_id: 用户ID
    - skip: 跳过记录数
    - limit: 查询记录数上限
    - start_date: 开始日期（可选）
    - end_date: 结束日期（可选）
    - action: 操作类型（可选，如"CREATE", "UPDATE", "DELETE"）
    - order: 排序方向（"asc"升序，"desc"降序）
    """
    query = db.query(AnnotationHistory).filter(AnnotationHistory.user_id == user_id)
    
    # 应用日期筛选
    if start_date:
        query = query.filter(AnnotationHistory.created_at >= start_date)
    if end_date:
        query = query.filter(AnnotationHistory.created_at <= end_date)
    
    # 应用操作类型筛选
    if action:
        query = query.filter(AnnotationHistory.action == action)
    
    # 应用排序
    if order.lower() == "asc":
        query = query.order_by(AnnotationHistory.created_at.asc())
    else:
        query = query.order_by(AnnotationHistory.created_at.desc())
    
    return query.offset(skip).limit(limit).all()

def get_history_by_id(db: Session, history_id: int) -> Optional[AnnotationHistory]:
    """
    通过ID获取历史记录
    """
    return db.query(AnnotationHistory).filter(AnnotationHistory.id == history_id).first()

def get_latest_annotation_history(db: Session, annotation_id: int) -> Optional[AnnotationHistory]:
    """
    获取标注的最新历史记录
    """
    return db.query(AnnotationHistory)\
        .filter(AnnotationHistory.annotation_id == annotation_id)\
        .order_by(AnnotationHistory.created_at.desc())\
        .first() 