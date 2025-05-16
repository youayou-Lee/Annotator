from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Body, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.task import TaskStatus, FieldType
from app.schemas.task import TaskCreate, Task, TaskUpdate, AnnotationFieldDef
import json
import tempfile
import os
import importlib.util
from pydantic import BaseModel, create_model, ValidationError
from pathlib import Path

router = APIRouter()

@router.post("/", response_model=Task)
def create_task(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    task_in: TaskCreate = Body(...)
):
    """
    创建标注任务
    """
    from app.services import task_service
    
    # 检查用户是否有权创建任务
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="没有足够权限创建任务"
        )
    
    # 使用服务创建任务
    task = task_service.create_task(db=db, task_in=task_in)
    return task

@router.post("/with-schema", response_model=Task)
async def create_task_with_schema(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    document_id: int = Form(...),
    annotator_id: int = Form(...),
    reviewer_id: Optional[int] = Form(None),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    annotation_fields_json: str = Form(..., description="JSON格式的标注字段定义"),
    validation_template: Optional[UploadFile] = File(None),
    document_path: Optional[str] = Form(None, description="公共文件库中的文档路径"),
    validation_template_path: Optional[str] = Form(None, description="公共文件库中的验证模板路径")
):
    """
    创建带数据模式的标注任务
    
    支持两种方式指定验证模板：
    1. 直接上传验证模板文件
    2. 提供公共文件库中的验证模板路径
    
    同样地，也支持两种方式指定文档：
    1. 通过document_id引用已存在的文档
    2. 通过document_path引用公共文件库中的文档
    """
    from app.services import task_service
    
    # 检查用户是否有权创建任务
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="没有足够权限创建任务"
        )
    
    # 解析标注字段定义
    try:
        annotation_fields = json.loads(annotation_fields_json)
        # 验证字段定义
        field_defs = []
        for field in annotation_fields:
            field_def = AnnotationFieldDef(**field)
            field_defs.append(field_def)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"标注字段定义格式无效: {str(e)}"
        )
    
    # 处理验证模板
    validation_template_path_final = None
    validation_schema = None
    
    # 如果提供了公共文件库中的验证模板路径
    if validation_template_path:
        # 公共文件目录路径
        ROOT_DIR = Path(os.path.abspath(__file__)).parent.parent.parent.parent.parent.parent
        PUBLIC_DIR = ROOT_DIR / "data" / "public"
        
        # 完整的模板文件路径
        if validation_template_path.startswith("templates/"):
            template_path = PUBLIC_DIR / validation_template_path
        else:
            template_path = PUBLIC_DIR / "templates" / validation_template_path
        
        if not os.path.exists(template_path):
            raise HTTPException(
                status_code=400,
                detail=f"验证模板文件不存在: {validation_template_path}"
            )
        
        validation_template_path_final = str(template_path)
        
        try:
            # 动态加载Python模块
            spec = importlib.util.spec_from_file_location("validation_module", validation_template_path_final)
            validation_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(validation_module)
            
            # 寻找BaseModel子类作为验证模式
            for attr_name in dir(validation_module):
                attr = getattr(validation_module, attr_name)
                if isinstance(attr, type) and issubclass(attr, BaseModel) and attr != BaseModel:
                    # 将模型转换为JSON模式
                    validation_schema = json.loads(attr.schema_json())
                    break
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"验证模板加载失败: {str(e)}"
            )
    # 如果直接上传了验证模板文件        
    elif validation_template:
        # 保存上传的Python文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
            temp_file.write(await validation_template.read())
            validation_template_path_final = temp_file.name
        
        try:
            # 动态加载Python模块
            spec = importlib.util.spec_from_file_location("validation_module", validation_template_path_final)
            validation_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(validation_module)
            
            # 寻找BaseModel子类作为验证模式
            for attr_name in dir(validation_module):
                attr = getattr(validation_module, attr_name)
                if isinstance(attr, type) and issubclass(attr, BaseModel) and attr != BaseModel:
                    # 将模型转换为JSON模式
                    validation_schema = json.loads(attr.schema_json())
                    break
            
            if not validation_schema:
                os.unlink(validation_template_path_final)
                raise HTTPException(
                    status_code=400,
                    detail="验证模板中未找到Pydantic模型"
                )
                
        except Exception as e:
            if os.path.exists(validation_template_path_final):
                os.unlink(validation_template_path_final)
            raise HTTPException(
                status_code=400,
                detail=f"验证模板加载失败: {str(e)}"
            )
    
    # 处理公共文件库中的文档
    if document_path:
        # 公共文件目录路径
        ROOT_DIR = Path(os.path.abspath(__file__)).parent.parent.parent.parent.parent.parent
        PUBLIC_DIR = ROOT_DIR / "data" / "public"
        
        # 完整的文档文件路径
        if document_path.startswith("documents/"):
            doc_path = PUBLIC_DIR / document_path
        else:
            doc_path = PUBLIC_DIR / "documents" / document_path
            
        if not os.path.exists(doc_path):
            raise HTTPException(
                status_code=400,
                detail=f"文档文件不存在: {document_path}"
            )
            
        # 处理文档：可以创建新的文档记录或检查是否已存在
        # 此处示例简化，实际应用中可能需要更复杂的处理
        from app.models.document import Document
        from app.schemas.document import DocumentCreate
        
        # 检查文档是否已存在
        existing_document = db.query(Document).filter(Document.file_path == str(doc_path)).first()
        if existing_document:
            document_id = existing_document.id
        else:
            # 创建新文档记录
            file_name = os.path.basename(doc_path)
            file_size = os.path.getsize(doc_path)
            file_type = os.path.splitext(file_name)[1].lstrip('.')
            
            doc_create = DocumentCreate(
                title=file_name,
                file_path=str(doc_path),
                file_name=file_name,
                file_type=file_type,
                file_size=file_size,
                user_id=current_user.id
            )
            
            new_document = Document(**doc_create.model_dump())
            db.add(new_document)
            db.commit()
            db.refresh(new_document)
            document_id = new_document.id
    
    # 从标注字段生成Pydantic模型（如果没有提供验证模板）
    if not validation_schema:
        field_definitions = {}
        for field in field_defs:
            # 根据字段类型确定Pydantic类型
            if field.type == FieldType.STRING:
                field_type = (str, ... if field.required else None)
            elif field.type == FieldType.INTEGER:
                field_type = (int, ... if field.required else None)
            elif field.type == FieldType.FLOAT:
                field_type = (float, ... if field.required else None)
            elif field.type == FieldType.BOOLEAN:
                field_type = (bool, ... if field.required else None)
            elif field.type == FieldType.ENUM and field.enum_values:
                # 对于枚举类型，我们使用Literal类型
                field_type = (str, ... if field.required else None)  # 简化处理
            else:
                field_type = (str, ... if field.required else None)  # 默认为字符串
                
            field_definitions[field.name] = field_type
        
        # 创建Pydantic模型并生成JSON模式
        model = create_model("GeneratedModel", **field_definitions)
        validation_schema = json.loads(model.schema_json())
    
    # 创建任务
    task_in = TaskCreate(
        document_id=document_id,
        annotator_id=annotator_id,
        reviewer_id=reviewer_id,
        user_id=current_user.id,
        title=title,
        description=description,
        annotation_fields=field_defs,
        validation_template=validation_template_path_final,
        validation_schema=validation_schema
    )
    
    from app.services import task_service
    task = task_service.create_task(db=db, task_in=task_in)
    return task

@router.get("/", response_model=List[Task])
def get_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    status: Optional[TaskStatus] = None
):
    """
    获取任务列表
    """
    from app.services import task_service
    tasks = task_service.get_tasks(
        db=db, 
        skip=skip, 
        limit=limit,
        status=status,
        user_id=None if current_user.is_superuser else current_user.id
    )
    return tasks

@router.get("/{task_id}", response_model=Task)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取任务详情
    """
    from app.services import task_service
    task = task_service.get_task(db=db, task_id=task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 检查权限（管理员可以查看所有任务，普通用户只能查看分配给自己的任务）
    if not current_user.is_superuser and task.annotator_id != current_user.id and task.reviewer_id != current_user.id:
        raise HTTPException(status_code=403, detail="没有权限访问此任务")
        
    return task

@router.put("/{task_id}", response_model=Task)
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新任务
    """
    from app.services import task_service
    task = task_service.get_task(db=db, task_id=task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 检查权限
    if not current_user.is_superuser and task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="没有权限修改此任务")
    
    updated_task = task_service.update_task(db=db, task_id=task_id, task_in=task_in)
    return updated_task

@router.delete("/{task_id}", response_model=Task)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除任务
    """
    from app.services import task_service
    task = task_service.get_task(db=db, task_id=task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 检查权限（只有管理员或创建者可以删除任务）
    if not current_user.is_superuser and task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="没有权限删除此任务")
    
    # 检查任务状态（已开始的任务不能删除）
    if task.status != TaskStatus.PENDING:
        raise HTTPException(status_code=400, detail="只能删除未开始的任务")
    
    deleted_task = task_service.delete_task(db=db, task_id=task_id)
    return deleted_task

@router.post("/{task_id}/validate-annotation")
def validate_annotation(
    task_id: int,
    annotation_data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    验证标注数据是否符合任务定义的格式要求
    """
    from app.services.task import validate_annotation_data
    
    # 获取任务
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 检查权限
    if not current_user.is_superuser and current_user.id != task.annotator_id and current_user.id != task.reviewer_id:
        raise HTTPException(status_code=403, detail="没有权限执行此操作")
    
    # 验证数据
    validation_result = validate_annotation_data(task_id, annotation_data, db)
    return validation_result

@router.post("/{task_id}/format-validation")
async def validate_document_format(
    task_id: int,
    document_data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    在标注前验证文档格式是否符合要求
    """
    # 获取任务
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 检查权限
    if not current_user.is_superuser and current_user.id != task.annotator_id and current_user.id != task.reviewer_id:
        raise HTTPException(status_code=403, detail="没有权限执行此操作")
    
    # 验证结果默认值
    result = {
        "valid": True,
        "errors": []
    }
    
    # 使用验证模板或验证模式验证文档格式
    if task.validation_schema:
        try:
            # 使用JSON模式验证
            from pydantic import create_model, ValidationError
            
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
            ValidationModel(**document_data)
            
        except ValidationError as e:
            result["valid"] = False
            result["errors"] = e.errors()
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"验证模式应用错误: {str(e)}")
    
    elif task.validation_template and os.path.exists(task.validation_template):
        try:
            # 动态加载模块
            import importlib.util
            import sys
            
            spec = importlib.util.spec_from_file_location(
                f"validation_module_{task_id}", 
                task.validation_template
            )
            validation_module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = validation_module
            spec.loader.exec_module(validation_module)
            
            # 查找验证函数
            if hasattr(validation_module, "validate_format"):
                validation_result = validation_module.validate_format(document_data)
                
                # 如果返回值是布尔值，转换为标准格式
                if isinstance(validation_result, bool):
                    result["valid"] = validation_result
                    if not validation_result:
                        result["errors"].append("文档格式验证失败")
                # 如果返回值是字典，使用其结果
                elif isinstance(validation_result, dict):
                    result = validation_result
            else:
                # 没有专门的格式验证函数，尝试使用常规验证
                if hasattr(validation_module, "validate_data"):
                    validation_result = validation_module.validate_data(document_data)
                    
                    if isinstance(validation_result, bool):
                        result["valid"] = validation_result
                        if not validation_result:
                            result["errors"].append("文档内容验证失败")
                    elif isinstance(validation_result, dict):
                        result = validation_result
                else:
                    # 尝试查找BaseModel
                    from pydantic import BaseModel
                    for attr_name in dir(validation_module):
                        attr = getattr(validation_module, attr_name)
                        if isinstance(attr, type) and issubclass(attr, BaseModel) and attr != BaseModel:
                            try:
                                # 使用BaseModel验证数据
                                attr(**document_data)
                            except ValidationError as e:
                                result["valid"] = False
                                result["errors"] = e.errors()
                            break
                            
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"验证模板执行错误: {str(e)}")
    
    return result

@router.post("/{task_id}/store-annotation")
async def store_annotation(
    task_id: int,
    annotation_data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    存储和持久化标注数据
    """
    from app.services import annotation_service
    
    # 获取任务
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 检查权限
    if not current_user.is_superuser and current_user.id != task.annotator_id:
        raise HTTPException(status_code=403, detail="没有权限执行此操作")
    
    # 首先验证数据
    from app.services.task import validate_annotation_data
    validation_result = validate_annotation_data(task_id, annotation_data, db)
    
    if not validation_result["valid"]:
        return {
            "success": False,
            "message": "数据验证失败，无法保存",
            "errors": validation_result["errors"]
        }
    
    # 存储标注数据
    try:
        annotation = annotation_service.create_or_update_annotation(
            db=db,
            task_id=task_id,
            user_id=current_user.id,
            data=annotation_data
        )
        
        # 如果任务状态是"待处理"，则更新为"进行中"
        if task.status == TaskStatus.PENDING:
            from app.services.task import update_task
            update_task(db, task_id=task_id, task_in=TaskUpdate(status=TaskStatus.IN_PROGRESS))
        
        return {
            "success": True,
            "message": "标注数据已保存",
            "annotation_id": annotation.id
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"保存标注数据时发生错误: {str(e)}"
        } 