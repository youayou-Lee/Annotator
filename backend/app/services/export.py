from typing import List, Optional, Dict, Any, Union
import json
import csv
import os
import time
import threading
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.export_task import ExportTask, ExportStatus, ExportFormat
from app.models.annotation import Annotation
from app.models.task import Task
from app.schemas.export_task import ExportTaskCreate, ExportTaskUpdate
from app.core.config import settings
from app.services.annotation import get_annotation
from app.services.task import get_task
from fastapi import HTTPException

def get_export_task(db: Session, export_task_id: int) -> Optional[ExportTask]:
    """获取导出任务"""
    return db.query(ExportTask).filter(ExportTask.id == export_task_id).first()

def get_export_tasks(
    db: Session,
    *,
    user_id: Optional[int] = None,
    status: Optional[ExportStatus] = None,
    skip: int = 0,
    limit: int = 100
) -> List[ExportTask]:
    """获取导出任务列表"""
    query = db.query(ExportTask)
    
    if user_id is not None:
        query = query.filter(ExportTask.user_id == user_id)
    
    if status is not None:
        query = query.filter(ExportTask.status == status)
    
    return query.order_by(ExportTask.created_at.desc()).offset(skip).limit(limit).all()

def create_export_task(
    db: Session,
    *,
    export_task_in: ExportTaskCreate
) -> ExportTask:
    """创建导出任务"""
    # 验证有效的任务ID或标注ID
    if not export_task_in.task_ids and not export_task_in.annotation_ids:
        raise HTTPException(status_code=400, detail="必须指定任务ID或标注ID")
    
    # 创建导出任务记录
    export_task_data = export_task_in.model_dump(exclude={"task_ids", "annotation_ids"})
    db_export_task = ExportTask(**export_task_data)
    db.add(db_export_task)
    db.commit()
    db.refresh(db_export_task)
    
    # 在后台线程中启动导出任务
    threading.Thread(
        target=process_export_task,
        args=(db_export_task.id, export_task_in.task_ids, export_task_in.annotation_ids, export_task_in.format),
        daemon=True
    ).start()
    
    return db_export_task

def update_export_task(
    db: Session,
    *,
    export_task_id: int,
    export_task_in: ExportTaskUpdate
) -> Optional[ExportTask]:
    """更新导出任务"""
    db_export_task = get_export_task(db, export_task_id)
    if not db_export_task:
        return None
    
    update_data = export_task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_export_task, field, value)
    
    db.add(db_export_task)
    db.commit()
    db.refresh(db_export_task)
    return db_export_task

def process_export_task(
    export_task_id: int,
    task_ids: Optional[List[int]],
    annotation_ids: Optional[List[int]],
    export_format: ExportFormat
):
    """处理导出任务（后台线程）"""
    # 创建一个新的数据库会话，因为这是在单独的线程中运行
    from app.db.session import SessionLocal
    db = SessionLocal()
    
    try:
        # 更新任务状态为处理中
        update_export_task(
            db,
            export_task_id=export_task_id,
            export_task_in=ExportTaskUpdate(status=ExportStatus.PROCESSING, progress=0.0)
        )
        
        # 准备导出数据
        export_data = []
        total_items = 0
        processed_items = 0
        
        # 如果指定了任务ID，导出所有任务相关标注
        if task_ids:
            for task_id in task_ids:
                task = get_task(db, task_id)
                if task:
                    # 获取任务相关的所有标注
                    annotations = db.query(Annotation).filter(Annotation.task_id == task_id).all()
                    total_items += len(annotations)
                    
                    for annotation in annotations:
                        export_data.append({
                            "task_id": task.id,
                            "task_title": task.title,
                            "annotation_id": annotation.id,
                            "annotation_type": annotation.annotation_type.value,
                            "content": annotation.content,
                            "status": annotation.status.value,
                            "created_at": annotation.created_at.isoformat(),
                            "updated_at": annotation.updated_at.isoformat()
                        })
                        
                        processed_items += 1
                        progress = (processed_items / total_items) * 100 if total_items > 0 else 0
                        
                        # 每处理10个项目更新一次进度，减少数据库操作
                        if processed_items % 10 == 0 or processed_items == total_items:
                            update_export_task(
                                db, 
                                export_task_id=export_task_id,
                                export_task_in=ExportTaskUpdate(progress=progress)
                            )
        
        # 如果指定了标注ID，仅导出这些标注
        if annotation_ids:
            for annotation_id in annotation_ids:
                annotation = get_annotation(db, annotation_id)
                if annotation:
                    task = get_task(db, annotation.task_id)
                    if task:
                        export_data.append({
                            "task_id": task.id,
                            "task_title": task.title,
                            "annotation_id": annotation.id,
                            "annotation_type": annotation.annotation_type.value,
                            "content": annotation.content,
                            "status": annotation.status.value,
                            "created_at": annotation.created_at.isoformat(),
                            "updated_at": annotation.updated_at.isoformat()
                        })
                
                total_items = len(annotation_ids)
                processed_items += 1
                progress = (processed_items / total_items) * 100 if total_items > 0 else 0
                
                # 每处理10个项目更新一次进度
                if processed_items % 10 == 0 or processed_items == total_items:
                    update_export_task(
                        db, 
                        export_task_id=export_task_id,
                        export_task_in=ExportTaskUpdate(progress=progress)
                    )
        
        # 确保导出目录存在
        export_dir = os.path.join(settings.UPLOAD_DIR, "exports")
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        
        # 生成导出文件名
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        file_name = f"export_{export_task_id}_{timestamp}"
        
        # 根据导出格式写入文件
        file_path = None
        
        if export_format == ExportFormat.JSON:
            file_path = os.path.join(export_dir, f"{file_name}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
                
        elif export_format == ExportFormat.JSONL:
            file_path = os.path.join(export_dir, f"{file_name}.jsonl")
            with open(file_path, "w", encoding="utf-8") as f:
                for item in export_data:
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")
                    
        elif export_format == ExportFormat.CSV:
            file_path = os.path.join(export_dir, f"{file_name}.csv")
            with open(file_path, "w", encoding="utf-8", newline="") as f:
                if export_data:
                    # 扁平化nested JSON结构
                    flattened_data = []
                    for item in export_data:
                        flat_item = {}
                        for k, v in item.items():
                            if k == "content" and isinstance(v, dict):
                                for content_k, content_v in v.items():
                                    flat_item[f"content_{content_k}"] = str(content_v)
                            else:
                                flat_item[k] = v
                        flattened_data.append(flat_item)
                    
                    writer = csv.DictWriter(f, fieldnames=flattened_data[0].keys())
                    writer.writeheader()
                    writer.writerows(flattened_data)
        
        # 更新任务状态为已完成
        update_export_task(
            db, 
            export_task_id=export_task_id,
            export_task_in=ExportTaskUpdate(
                status=ExportStatus.COMPLETED,
                progress=100.0,
                file_path=file_path,
                completed_at=datetime.utcnow()
            )
        )
        
    except Exception as e:
        # 更新任务状态为失败
        update_export_task(
            db, 
            export_task_id=export_task_id,
            export_task_in=ExportTaskUpdate(
                status=ExportStatus.FAILED,
                error_message=str(e)
            )
        )
    
    finally:
        db.close()

def delete_export_task(db: Session, export_task_id: int) -> Optional[ExportTask]:
    """删除导出任务"""
    db_export_task = get_export_task(db, export_task_id)
    if not db_export_task:
        return None
    
    # 如果有导出文件，删除文件
    if db_export_task.file_path and os.path.exists(db_export_task.file_path):
        try:
            os.remove(db_export_task.file_path)
        except:
            pass  # 忽略文件删除错误
    
    # 删除记录
    db.delete(db_export_task)
    db.commit()
    return db_export_task 