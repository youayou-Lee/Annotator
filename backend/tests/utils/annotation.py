from typing import Optional, Dict

from sqlalchemy.orm import Session

from app.services.annotation import create_annotation
from app.schemas.annotation import AnnotationCreate
from app.models.annotation import Annotation, AnnotationType
from tests.utils.utils import random_lower_string

def create_random_annotation(
    db: Session, 
    task_id: int, 
    annotator_id: int, 
    annotation_type: AnnotationType = AnnotationType.TEXT,
    content: Optional[Dict] = None
) -> Annotation:
    """创建一个随机标注"""
    if not content:
        if annotation_type == AnnotationType.TEXT:
            content = {
                "text": random_lower_string(),
                "start_offset": 0,
                "end_offset": 10,
                "label": random_lower_string()
            }
        # 可以添加其他类型的标注内容生成逻辑
        
    annotation_in = AnnotationCreate(
        task_id=task_id,
        annotator_id=annotator_id,
        annotation_type=annotation_type,
        content=content
    )
    return create_annotation(db=db, annotation_in=annotation_in) 