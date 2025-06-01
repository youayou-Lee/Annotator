from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, Optional
from pydantic import BaseModel

from ..models.user import UserInDB, UserRole
from ..models.annotation import (
    Annotation, AnnotationCreate, AnnotationUpdate, 
    AnnotationSubmit, AnnotationReview, AnnotationStatus
)
from ..core.security import get_current_user
from ..core.storage import StorageManager
from ..core.annotation_validator import AnnotationValidator

router = APIRouter()
storage = StorageManager()
annotation_validator = AnnotationValidator()


class AnnotationValidationRequest(BaseModel):
    """标注数据验证请求"""
    template_file_path: str
    annotation_data: Dict[str, Any]


class AnnotationValidationResponse(BaseModel):
    """标注数据验证响应"""
    valid: bool
    error: Optional[str] = None
    error_details: Optional[list] = None
    validated_data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class PartialValidationRequest(BaseModel):
    """部分数据验证请求"""
    template_file_path: str
    partial_data: Dict[str, Any]


class PartialValidationResponse(BaseModel):
    """部分数据验证响应"""
    valid: bool
    error: Optional[str] = None
    field_results: Optional[Dict[str, Any]] = None


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
            updated_at=datetime.now()
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
    """保存标注数据"""
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
            updated_at=datetime.now()
        )
    
    # 更新标注数据
    if annotation_update.annotated_data is not None:
        annotation.annotated_data = annotation_update.annotated_data
    
    if annotation_update.status is not None:
        annotation.status = annotation_update.status
    
    annotation.updated_at = datetime.now()
    
    return storage.save_annotation(annotation)


@router.post("/{task_id}/documents/{document_id}/submit", response_model=Annotation, summary="提交标注")
async def submit_annotation(
    task_id: str,
    document_id: str,
    annotation_submit: AnnotationSubmit,
    current_user: UserInDB = Depends(get_current_user)
):
    """提交标注"""
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
    
    # 获取或创建标注数据
    annotation = storage.get_annotation(task_id, document_id)
    if not annotation:
        annotation = Annotation(
            document_id=document_id,
            task_id=task_id,
            status=AnnotationStatus.COMPLETED,
            annotator_id=current_user.id,
            updated_at=datetime.now()
        )
    
    # 更新标注数据
    annotation.annotated_data = annotation_submit.annotated_data
    annotation.status = AnnotationStatus.COMPLETED
    annotation.updated_at = datetime.now()
    
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