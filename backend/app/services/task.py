from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate
from fastapi import HTTPException
import importlib.util
import sys
import tempfile
import os
import json
from pydantic import BaseModel, ValidationError, create_model

def get_task(db: Session, task_id: int) -> Optional[Task]:
    return db.query(Task).filter(Task.id == task_id).first()

def get_tasks(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    annotator_id: Optional[int] = None,
    reviewer_id: Optional[int] = None,
    status: Optional[TaskStatus] = None
) -> List[Task]:
    query = db.query(Task)
    if annotator_id is not None:
        query = query.filter(Task.annotator_id == annotator_id)
    if reviewer_id is not None:
        query = query.filter(Task.reviewer_id == reviewer_id)
    if status is not None:
        query = query.filter(Task.status == status)
    return query.offset(skip).limit(limit).all()

def create_task(db: Session, *, task_in: TaskCreate) -> Task:
    db_task = Task(**task_in.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(
    db: Session,
    *,
    task_id: int,
    task_in: TaskUpdate
) -> Optional[Task]:
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    
    update_data = task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int) -> Optional[Task]:
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    
    db.delete(db_task)
    db.commit()
    return db_task

def validate_annotation_data(
    task_id: int,
    annotation_data: Dict[str, Any],
    db: Session
) -> Dict[str, Any]:
    """
    使用任务的验证模板或模式验证标注数据
    
    Args:
        task_id: 任务ID
        annotation_data: 待验证的标注数据字典
        db: 数据库会话
        
    Returns:
        验证结果，包含是否有效及错误信息
    """
    task = get_task(db, task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 结果默认值
    result = {
        "valid": True,
        "errors": []
    }
    
    # 1. 如果有Python验证模板，优先使用
    if task.validation_template and os.path.exists(task.validation_template):
        try:
            # 动态加载模块
            spec = importlib.util.spec_from_file_location(
                f"validation_module_{task_id}", 
                task.validation_template
            )
            validation_module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = validation_module
            spec.loader.exec_module(validation_module)
            
            # 查找验证函数
            if hasattr(validation_module, "validate_data"):
                validation_result = validation_module.validate_data(annotation_data)
                
                # 如果返回值是布尔值，转换为标准格式
                if isinstance(validation_result, bool):
                    result["valid"] = validation_result
                    if not validation_result:
                        result["errors"].append("数据验证失败")
                # 如果返回值是字典，使用其结果
                elif isinstance(validation_result, dict):
                    result = validation_result
            else:
                # 没有验证函数，尝试查找BaseModel
                for attr_name in dir(validation_module):
                    attr = getattr(validation_module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, BaseModel) and attr != BaseModel:
                        try:
                            # 使用BaseModel验证数据
                            attr(**annotation_data)
                        except ValidationError as e:
                            result["valid"] = False
                            result["errors"] = e.errors()
                        break
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"验证模板执行错误: {str(e)}")
    
    # 2. 如果没有Python模板或模板执行失败但有JSON模式定义，使用JSON模式
    elif task.validation_schema:
        try:
            # 根据JSON模式动态创建Pydantic模型
            field_definitions = {}
            
            for field_name, field_def in task.validation_schema.get("properties", {}).items():
                field_type = str  # 默认类型
                
                # 根据JSON模式的类型确定Python类型
                schema_type = field_def.get("type", "string")
                if schema_type == "integer":
                    field_type = int
                elif schema_type == "number":
                    field_type = float
                elif schema_type == "boolean":
                    field_type = bool
                
                # 检查是否必填
                required = field_name in task.validation_schema.get("required", [])
                field_definitions[field_name] = (field_type, ... if required else None)
            
            # 创建动态模型
            ValidationModel = create_model(
                f"DynamicModel_{task_id}",
                **field_definitions
            )
            
            # 验证数据
            ValidationModel(**annotation_data)
            
        except ValidationError as e:
            result["valid"] = False
            result["errors"] = e.errors()
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"验证模式应用错误: {str(e)}")
    
    # 3. 如果没有验证模板也没有JSON模式，使用任务定义的字段进行基本验证
    elif task.annotation_fields:
        try:
            field_definitions = {}
            
            for field in task.annotation_fields:
                field_type = str  # 默认类型
                
                # 根据字段类型确定Python类型
                if field.type == "integer":
                    field_type = int
                elif field.type == "float":
                    field_type = float
                elif field.type == "boolean":
                    field_type = bool
                
                field_definitions[field.name] = (field_type, ... if field.required else None)
            
            # 创建动态模型
            ValidationModel = create_model(
                f"FieldModel_{task_id}",
                **field_definitions
            )
            
            # 验证数据
            ValidationModel(**annotation_data)
            
        except ValidationError as e:
            result["valid"] = False
            result["errors"] = e.errors()
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"字段验证错误: {str(e)}")
    
    return result 