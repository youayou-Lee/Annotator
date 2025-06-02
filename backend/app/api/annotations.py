from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import json

from ..models.user import UserInDB, UserRole
from ..models.annotation import (
    Annotation, AnnotationCreate, AnnotationUpdate, 
    AnnotationSubmit, AnnotationReview, AnnotationStatus
)
from ..models.task import DocumentStatus
from ..core.security import get_current_user
from ..core.storage import StorageManager
from ..core.annotation_validator import AnnotationValidator

router = APIRouter()
storage = StorageManager()
annotation_validator = AnnotationValidator()


class AnnotationValidationRequest(BaseModel):
    """标注数据验证请求 - 已注释，待重写"""
    template_file_path: str
    annotation_data: Dict[str, Any]


class AnnotationValidationResponse(BaseModel):
    """标注数据验证响应 - 已注释，待重写"""
    valid: bool
    error: Optional[str] = None
    error_details: Optional[list] = None
    validated_data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class PartialValidationRequest(BaseModel):
    """部分数据验证请求 - 已注释，待重写"""
    template_file_path: str
    partial_data: Dict[str, Any]


class PartialValidationResponse(BaseModel):
    """部分数据验证响应 - 已注释，待重写"""
    valid: bool
    error: Optional[str] = None
    field_results: Optional[Dict[str, Any]] = None


class DocumentListItem(BaseModel):
    """文档列表项"""
    document_id: str
    document_name: str
    document_path: str
    status: DocumentStatus
    last_modified: Optional[datetime] = None
    completion_percentage: float = 0.0


class DocumentListResponse(BaseModel):
    """文档列表响应"""
    documents: List[DocumentListItem]
    total_count: int
    completed_count: int
    in_progress_count: int
    pending_count: int


class DocumentContentResponse(BaseModel):
    """文档内容响应"""
    document_id: str
    content: Dict[str, Any]
    formatted_content: str


class FormFieldConfig(BaseModel):
    """表单字段配置"""
    path: str
    field_type: str
    required: bool
    description: str = ""
    constraints: Dict[str, Any] = {}
    default_value: Any = None
    options: Optional[List[Any]] = None  # 用于枚举类型


class FormConfigResponse(BaseModel):
    """表单配置响应"""
    fields: List[FormFieldConfig]
    template_info: Dict[str, Any] = {}


class TaskProgressResponse(BaseModel):
    """任务进度响应"""
    task_id: str
    total_documents: int
    completed_documents: int
    in_progress_documents: int
    pending_documents: int
    completion_percentage: float
    current_document_progress: Optional[Dict[str, Any]] = None


@router.get("/{task_id}/documents", response_model=DocumentListResponse, summary="获取任务文档列表")
async def get_task_documents(
    task_id: str,
    status_filter: Optional[DocumentStatus] = Query(None, description="按状态过滤"),
    current_user: UserInDB = Depends(get_current_user)
):
    """获取任务包含的所有文档列表"""
    # 检查任务权限
    task = storage.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    if current_user.role == UserRole.ANNOTATOR and task.assignee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此任务"
        )
    
    # 构建文档列表
    documents = []
    for doc in task.documents:
        # 应用状态过滤
        if status_filter and doc.status != status_filter:
            continue
            
        # 获取标注数据以计算完成百分比
        annotation = storage.get_annotation(task_id, doc.id)
        completion_percentage = 0.0
        last_modified = None
        
        if annotation:
            last_modified = annotation.updated_at
            # 简单的完成度计算：有标注数据且状态为已完成则100%，进行中则50%
            if annotation.status == AnnotationStatus.COMPLETED:
                completion_percentage = 100.0
            elif annotation.status == AnnotationStatus.IN_PROGRESS:
                completion_percentage = 50.0
        
        documents.append(DocumentListItem(
            document_id=doc.id,
            document_name=doc.filename,
            document_path=doc.file_path,
            status=doc.status,
            last_modified=last_modified,
            completion_percentage=completion_percentage
        ))
    
    # 统计各状态数量
    total_count = len(documents)
    completed_count = sum(1 for doc in documents if doc.status == DocumentStatus.COMPLETED)
    in_progress_count = sum(1 for doc in documents if doc.status == DocumentStatus.IN_PROGRESS)
    pending_count = sum(1 for doc in documents if doc.status == DocumentStatus.PENDING)
    
    return DocumentListResponse(
        documents=documents,
        total_count=total_count,
        completed_count=completed_count,
        in_progress_count=in_progress_count,
        pending_count=pending_count
    )


@router.get("/{task_id}/documents/{document_id}/content", response_model=DocumentContentResponse, summary="获取文档内容")
async def get_document_content(
    task_id: str,
    document_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """获取原始JSON文档内容"""
    # 检查任务权限
    task = storage.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    if current_user.role == UserRole.ANNOTATOR and task.assignee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此任务"
        )
    
    # 查找文档
    document = None
    for doc in task.documents:
        if doc.id == document_id:
            document = doc
            break
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )
    
    # 读取文档内容
    content_str = storage.get_file_content(document.file_path)
    if content_str is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档文件不存在"
        )
    
    try:
        # 解析JSON内容
        content = json.loads(content_str)
        
        # 如果内容是数组，包装成对象
        if isinstance(content, list):
            content = {"items": content, "type": "array", "count": len(content)}
        
        # 格式化内容用于显示
        formatted_content = json.dumps(content, ensure_ascii=False, indent=2)
        
        return DocumentContentResponse(
            document_id=document_id,
            content=content,
            formatted_content=formatted_content
        )
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文档格式错误: {str(e)}"
        )


@router.get("/{task_id}/documents/{document_id}/form-config", response_model=FormConfigResponse, summary="获取标注表单配置")
async def get_form_config(
    task_id: str,
    document_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """根据模板动态生成表单字段配置"""
    # 检查任务权限
    task = storage.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    if current_user.role == UserRole.ANNOTATOR and task.assignee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此任务"
        )
    
    # 检查文档是否存在
    document = None
    for doc in task.documents:
        if doc.id == document_id:
            document = doc
            break
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )
    
    # 如果任务没有模板，返回空配置
    if not task.template or not task.template.file_path:
        return FormConfigResponse(
            fields=[],
            template_info={"message": "此任务未配置模板"}
        )
    
    try:
        # 使用简化版文档校验模块解析模板
        import sys
        from pathlib import Path
        
        # 添加项目根目录到Python路径
        project_root = Path(__file__).parent.parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        from simple_document_validator import SimpleDocumentValidator
        
        # 构建完整的模板文件路径
        template_full_path = storage.data_dir / task.template.file_path
        
        validator = SimpleDocumentValidator(str(template_full_path))
        if not validator.main_model:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="模板文件无效"
            )
        
        # 获取标注字段配置
        annotation_schema = validator.get_annotation_schema()
        
        # 转换为前端表单配置格式
        fields = []
        for field_schema in annotation_schema:
            field_config = FormFieldConfig(
                path=field_schema["path"],
                field_type=field_schema["type"],
                required=field_schema["required"],
                description=field_schema.get("description", ""),
                constraints=field_schema.get("constraints", {}),
                default_value=field_schema.get("default"),
                options=field_schema.get("options")
            )
            fields.append(field_config)
        
        template_info = {
            "template_path": task.template.file_path,
            "main_model": validator.main_model.__name__,
            "fields_count": len(fields)
        }
        
        return FormConfigResponse(
            fields=fields,
            template_info=template_info
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成表单配置失败: {str(e)}"
        )


@router.get("/{task_id}/progress", response_model=TaskProgressResponse, summary="获取任务进度统计")
async def get_task_progress(
    task_id: str,
    current_document_id: Optional[str] = Query(None, description="当前文档ID"),
    current_user: UserInDB = Depends(get_current_user)
):
    """获取整体任务进度和当前文档进度"""
    # 检查任务权限
    task = storage.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    if current_user.role == UserRole.ANNOTATOR and task.assignee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此任务"
        )
    
    # 计算整体进度
    total_documents = len(task.documents)
    completed_documents = sum(1 for doc in task.documents if doc.status == DocumentStatus.COMPLETED)
    in_progress_documents = sum(1 for doc in task.documents if doc.status == DocumentStatus.IN_PROGRESS)
    pending_documents = sum(1 for doc in task.documents if doc.status == DocumentStatus.PENDING)
    
    completion_percentage = (completed_documents / total_documents * 100) if total_documents > 0 else 0.0
    
    # 获取当前文档进度
    current_document_progress = None
    if current_document_id:
        annotation = storage.get_annotation(task_id, current_document_id)
        if annotation:
            current_document_progress = {
                "document_id": current_document_id,
                "status": annotation.status.value,
                "last_updated": annotation.updated_at,
                "has_data": bool(annotation.annotation_data)
            }
    
    return TaskProgressResponse(
        task_id=task_id,
        total_documents=total_documents,
        completed_documents=completed_documents,
        in_progress_documents=in_progress_documents,
        pending_documents=pending_documents,
        completion_percentage=round(completion_percentage, 2),
        current_document_progress=current_document_progress
    )


@router.get("/{task_id}/documents/{document_id}/annotation", response_model=Annotation, summary="获取标注数据")
async def get_annotation(
    task_id: str,
    document_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """获取标注数据"""
    # 检查任务权限
    task = storage.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    if current_user.role == UserRole.ANNOTATOR and task.assignee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此任务"
        )
    
    # 获取标注数据
    annotation = storage.get_annotation(task_id, document_id)
    if not annotation:
        # 如果不存在，创建新的标注记录
        annotation = Annotation(
            document_id=document_id,
            task_id=task_id,
            status=AnnotationStatus.PENDING,
            annotator_id=current_user.id,
            updated_at=datetime.now(),
            annotation_data={}
        )
        storage.save_annotation(annotation)
    
    return annotation


@router.post("/{task_id}/documents/{document_id}/annotation", response_model=Annotation, summary="保存标注数据")
async def save_annotation(
    task_id: str,
    document_id: str,
    annotation_update: AnnotationUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    """保存标注数据（支持自动保存和手动保存）"""
    # 检查任务权限
    task = storage.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    if current_user.role == UserRole.ANNOTATOR and task.assignee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此任务"
        )
    
    # 获取或创建标注数据
    annotation = storage.get_annotation(task_id, document_id)
    if not annotation:
        annotation = Annotation(
            document_id=document_id,
            task_id=task_id,
            status=AnnotationStatus.IN_PROGRESS,
            annotator_id=current_user.id,
            updated_at=datetime.now(),
            annotation_data={}
        )
    
    # 更新标注数据
    if annotation_update.annotation_data is not None:
        annotation.annotation_data = annotation_update.annotation_data
        # 如果有数据且状态还是pending，自动改为in_progress
        if annotation.status == AnnotationStatus.PENDING:
            annotation.status = AnnotationStatus.IN_PROGRESS
    
    if annotation_update.status is not None:
        annotation.status = annotation_update.status
    
    annotation.updated_at = datetime.now()
    
    # 同步更新任务中的文档状态
    if annotation.status == AnnotationStatus.COMPLETED:
        storage.update_document_status(task_id, document_id, DocumentStatus.COMPLETED)
    elif annotation.status == AnnotationStatus.IN_PROGRESS:
        storage.update_document_status(task_id, document_id, DocumentStatus.IN_PROGRESS)
    
    return storage.save_annotation(annotation)


@router.post("/{task_id}/documents/{document_id}/submit", response_model=Annotation, summary="提交文档标注")
async def submit_annotation(
    task_id: str,
    document_id: str,
    annotation_submit: AnnotationSubmit,
    current_user: UserInDB = Depends(get_current_user)
):
    """提交标注（标记文档为已完成状态）"""
    # 检查任务权限
    task = storage.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    if task.assignee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能提交分配给自己的任务"
        )
    
    # 如果任务有模板，进行提交前验证
    if task.template and task.template.file_path:
        try:
            import sys
            from pathlib import Path
            
            # 添加项目根目录到Python路径
            project_root = Path(__file__).parent.parent.parent.parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
            
            from simple_document_validator import SimpleDocumentValidator
            
            # 构建完整的模板文件路径
            template_full_path = storage.data_dir / task.template.file_path
            
            validator = SimpleDocumentValidator(str(template_full_path))
            validation_result = validator.validate_document(annotation_submit.annotation_data)
            
            if not validation_result["valid"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"标注数据验证失败: {validation_result.get('errors', '未知错误')}"
                )
        except Exception as e:
            # 如果验证失败，记录错误但不阻止提交
            print(f"模板验证失败: {str(e)}")
    
    # 获取或创建标注数据
    annotation = storage.get_annotation(task_id, document_id)
    if not annotation:
        annotation = Annotation(
            document_id=document_id,
            task_id=task_id,
            status=AnnotationStatus.COMPLETED,
            annotator_id=current_user.id,
            updated_at=datetime.now(),
            annotation_data=annotation_submit.annotation_data
        )
    else:
        # 更新标注数据
        annotation.annotation_data = annotation_submit.annotation_data
        annotation.status = AnnotationStatus.COMPLETED
        annotation.updated_at = datetime.now()
    
    # 同步更新任务中的文档状态
    storage.update_document_status(task_id, document_id, DocumentStatus.COMPLETED)
    
    return storage.save_annotation(annotation)


@router.get("/{task_id}/documents/{document_id}/review", response_model=Annotation, summary="获取复审数据")
async def get_review(
    task_id: str,
    document_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """获取复审数据"""
    # 检查权限
    if current_user.role == UserRole.ANNOTATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="标注员无权进行复审"
        )
    
    annotation = storage.get_annotation(task_id, document_id)
    if not annotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标注数据不存在"
        )
    
    return annotation


@router.post("/{task_id}/documents/{document_id}/review", response_model=Annotation, summary="提交复审")
async def submit_review(
    task_id: str,
    document_id: str,
    review: AnnotationReview,
    current_user: UserInDB = Depends(get_current_user)
):
    """提交复审"""
    # 检查权限
    if current_user.role == UserRole.ANNOTATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="标注员无权进行复审"
        )
    
    annotation = storage.get_annotation(task_id, document_id)
    if not annotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标注数据不存在"
        )
    
    # 更新复审信息
    annotation.reviewer_id = current_user.id
    annotation.reviewed_at = datetime.now()
    annotation.status = AnnotationStatus.REVIEWED
    
    if review.revised_data:
        annotation.annotated_data = review.revised_data
    
    annotation.updated_at = datetime.now()
    
    return storage.save_annotation(annotation)


@router.post("/validate", response_model=AnnotationValidationResponse, summary="验证标注数据")
async def validate_annotation_data(
    request: AnnotationValidationRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """验证标注数据是否符合模板定义"""
    try:
        # 构建完整的模板文件路径
        full_template_path = storage.data_dir / request.template_file_path
        
        # 验证数据
        validation_result = annotation_validator.validate_annotation_data(
            str(full_template_path), 
            request.annotation_data
        )
        
        return AnnotationValidationResponse(**validation_result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"验证过程中发生错误: {str(e)}"
        )


@router.post("/validate-partial", response_model=PartialValidationResponse, summary="验证部分标注数据")
async def validate_partial_annotation_data(
    request: PartialValidationRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """验证部分标注数据（用于实时验证）"""
    try:
        # 构建完整的模板文件路径
        full_template_path = storage.data_dir / request.template_file_path
        
        # 验证部分数据
        validation_result = annotation_validator.validate_partial_data(
            str(full_template_path), 
            request.partial_data
        )
        
        return PartialValidationResponse(**validation_result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"部分验证过程中发生错误: {str(e)}"
        )


@router.get("/{task_id}/{document_id}", response_model=Annotation, summary="获取标注数据")
async def get_annotation_by_task_and_document(
    task_id: str,
    document_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """获取指定任务和文档的标注数据"""
    annotation = storage.get_annotation(task_id, document_id)
    if not annotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标注数据不存在"
        )
    return annotation


@router.post("/{task_id}/{document_id}", response_model=Annotation, summary="保存标注数据")
async def save_annotation_by_task_and_document(
    task_id: str,
    document_id: str,
    annotation_data: Dict[str, Any],
    current_user: UserInDB = Depends(get_current_user)
):
    """保存标注数据"""
    try:
        # 获取任务信息以获取模板路径
        task = storage.get_task_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="任务不存在"
            )
        
        # 如果任务有模板，验证数据
        if task.template and task.template.file_path:
            full_template_path = storage.data_dir / task.template.file_path
            validation_result = annotation_validator.validate_annotation_data(
                str(full_template_path), 
                annotation_data
            )
            
            if not validation_result["valid"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "message": "标注数据验证失败",
                        "error": validation_result.get("error"),
                        "error_details": validation_result.get("error_details")
                    }
                )
            
            # 使用验证后的数据
            annotation_data = validation_result.get("validated_data", annotation_data)
        
        # 创建或更新标注
        annotation = Annotation(
            task_id=task_id,
            document_id=document_id,
            annotator_id=current_user.id,
            annotation_data=annotation_data
        )
        
        saved_annotation = storage.save_annotation(annotation)
        return saved_annotation
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"保存标注数据失败: {str(e)}"
        )


@router.put("/{task_id}/{document_id}", response_model=Annotation, summary="更新标注数据")
async def update_annotation_by_task_and_document(
    task_id: str,
    document_id: str,
    annotation_data: Dict[str, Any],
    current_user: UserInDB = Depends(get_current_user)
):
    """更新标注数据"""
    try:
        # 检查标注是否存在
        existing_annotation = storage.get_annotation(task_id, document_id)
        if not existing_annotation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="标注数据不存在"
            )
        
        # 检查权限（只有标注者本人或管理员可以修改）
        if (existing_annotation.annotator_id != current_user.id and 
            current_user.role not in ["admin", "super_admin"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限修改此标注"
            )
        
        # 获取任务信息以获取模板路径
        task = storage.get_task_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="任务不存在"
            )
        
        # 如果任务有模板，验证数据
        if task.template and task.template.file_path:
            full_template_path = storage.data_dir / task.template.file_path
            validation_result = annotation_validator.validate_annotation_data(
                str(full_template_path), 
                annotation_data
            )
            
            if not validation_result["valid"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "message": "标注数据验证失败",
                        "error": validation_result.get("error"),
                        "error_details": validation_result.get("error_details")
                    }
                )
            
            # 使用验证后的数据
            annotation_data = validation_result.get("validated_data", annotation_data)
        
        # 更新标注数据
        existing_annotation.annotation_data = annotation_data
        updated_annotation = storage.save_annotation(existing_annotation)
        return updated_annotation
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新标注数据失败: {str(e)}"
        )


@router.delete("/{task_id}/{document_id}", summary="删除标注数据")
async def delete_annotation_by_task_and_document(
    task_id: str,
    document_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """删除标注数据"""
    try:
        # 检查标注是否存在
        existing_annotation = storage.get_annotation(task_id, document_id)
        if not existing_annotation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="标注数据不存在"
            )
        
        # 检查权限（只有标注者本人或管理员可以删除）
        if (existing_annotation.annotator_id != current_user.id and 
            current_user.role not in ["admin", "super_admin"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限删除此标注"
            )
        
        # 删除标注文件
        annotation_file = storage.data_dir / "tasks" / task_id / "annotations" / f"{document_id}.json"
        if annotation_file.exists():
            annotation_file.unlink()
        
        return {"message": "标注数据删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除标注数据失败: {str(e)}"
        ) 