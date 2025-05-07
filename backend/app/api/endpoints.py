from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import List, Dict, Any, Optional
from ..models.document import Document
from ..services.filter_service import FilterService
from ..services.format_service import FormatService
from ..services.annotator_service import AnnotatorService
from ..services.ai_review_service import AIReviewService
from ..services.training_service import TrainingService
from ..services.file_service import FileService
from ..services.task_service import TaskService
from datetime import datetime
import json
import os
from ..models.task import TaskConfig

router = APIRouter()

# 依赖注入
def get_filter_service():
    return FilterService()

def get_format_service():
    return FormatService("data/formatted")

def get_annotator_service():
    return AnnotatorService("data/annotations")

def get_ai_review_service():
    return AIReviewService("your-api-key", "data/ai_reviews")

def get_training_service():
    return TrainingService("data/training")

def get_file_service():
    return FileService("data/upload")

def get_task_service():
    return TaskService(upload_dir="data/upload", task_templates_dir="data/task_templates")

# 格式化服务路由
@router.get("/format/template")
def get_default_format_template(
    format_service: FormatService = Depends(get_format_service)
):
    """获取格式化模板"""
    try:
        templates = format_service.get_default_template()
        return {"templates": templates}  # 修改返回格式为包含 templates 键的字典
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"无法读取默认模板: {str(e)}")

@router.get("/format/template/{template_name}/content")
async def get_format_template_content(
    template_name: str,
    format_service: FormatService = Depends(get_format_service)
):
    """获取指定格式化模板的内容"""
    try:
        # 构建模板文件路径
        template_path = os.path.join("data", "format_templates", template_name)
        
        # 检查文件是否存在
        if not os.path.exists(template_path):
            raise HTTPException(
                status_code=404,
                detail=f"模板文件 {template_name} 不存在"
            )
            
        # 读取模板文件内容
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        return {
            "name": template_name,
            "content": content,
            "type": "python"
        }
            
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"读取模板内容失败: {str(e)}"
        )

@router.post("/format/process")
async def process_jsonl_file(
    jsonl_file: UploadFile = File(...),
    template_file: UploadFile = None,
    format_service: FormatService = Depends(get_format_service)
):
    """处理JSONL文件，根据模板进行格式化"""
    try:
        result = await format_service.process_file(jsonl_file, template_file)
        return {
            "success": True,
            "message": "文件处理成功",
            "document_count": result["document_count"],
            "success_count": result["success_count"],
            "error_count": result["error_count"],
            "output_path": result["output_path"]
        }
    except Exception as e:
        print(f"处理JSONL文件失败: {str(e)}")  # 添加日志输出
        raise HTTPException(status_code=500, detail=str(e))

# 文件上传
@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    file_service: FileService = Depends(get_file_service)
):
    try:
        print(f"开始处理文件上传: {file.filename}")
        
        # 检查文件类型
        if not file.filename.endswith(('.json', '.jsonl')):
            raise HTTPException(
                status_code=400,
                detail="只支持上传JSON或JSONL格式的文件"
            )
        
        # 检查文件大小（限制为100MB）
        content = await file.read()
        
        # 保存上传的文件
        saved_filename = await file_service.save_upload_file(file, content)
        
        return {
            "code": 200,
            "message": "文件上传成功",
            "filename": saved_filename
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"上传文件时出错: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"上传文件时出错: {str(e)}"
        )

# 获取可用文件列表
@router.get("/files")
async def get_available_files(
    filter_service: FilterService = Depends(get_filter_service)
):
    try:
        files = filter_service.get_available_files()
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 获取可用模板列表
@router.get("/templates")
async def get_available_templates(
    task_service: TaskService = Depends(get_task_service)
):
    try:
        templates = task_service.get_available_templates()
        return {"templates": templates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates/{template_name}/content")
async def get_template_content(template_name: str):
    """获取指定模板的内容"""
    try:
        template_path = f"data/task_templates/{template_name}"
        with open(template_path, "r", encoding="utf-8") as f:
            content = json.load(f)
        return content
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="模板文件不存在")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="模板文件格式错误")

# 获取可用的格式化模板列表
@router.get("/format_templates")
async def get_available_format_templates():
    """获取可用的格式化模板列表"""
    try:
        templates_dir = os.path.join("data", "format_templates")
        templates = []
        if (os.path.exists(templates_dir)):
            for filename in os.listdir(templates_dir):
                if filename.endswith('.py'):
                    templates.append(filename)
        return {"templates": templates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 格式化模板上传
@router.post("/upload_format_template")
async def upload_format_template(
    file: UploadFile = File(...),
    file_service: FileService = Depends(get_file_service)
):
    try:
        print(f"开始处理格式化模板上传: {file.filename}")
        
        # 检查文件类型
        if not file.filename.endswith('.py'):
            raise HTTPException(
                status_code=400,
                detail="只支持上传 Python (.py) 格式的模板文件"
            )
        
        # 检查文件大小（限制为1MB）
        content = await file.read()
        if len(content) > 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="模板文件大小不能超过1MB"
            )
        
        # 验证Python语法
        try:
            compile(content.decode('utf-8'), file.filename, 'exec')
        except SyntaxError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Python语法错误: {str(e)}"
            )
        
        # 保存模板文件到格式化模板目录
        templates_dir = os.path.join("data", "format_templates")
        os.makedirs(templates_dir, exist_ok=True)
        
        file_path = os.path.join(templates_dir, file.filename)
        with open(file_path, 'wb') as f:
            f.write(content)
        
        return {
            "code": 200,
            "message": "格式化模板上传成功",
            "filename": file.filename
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"上传格式化模板时出错: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"上传格式化模板时出错: {str(e)}"
        )

# 文档过滤
@router.post("/filter")
async def filter_documents(
    file_names: List[str],
    filter_conditions: Dict[str, Any],
    filter_service: FilterService = Depends(get_filter_service)
):
    try:
        # 加载文档
        documents = filter_service.load_documents_from_files(file_names)
        
        # 应用过滤条件
        filtered_docs = filter_service.apply_filters(documents, filter_conditions)
        
        # 保存过滤结果
        output_file = f"filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        output_path = filter_service.save_filtered_documents(filtered_docs, output_file)
        
        return {
            "filtered_documents": filtered_docs,
            "output_file": output_file,
            "document_count": len(filtered_docs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 格式化存储
@router.post("/format")
async def format_documents(
    documents: List[Document],
    template: Dict[str, Any],
    filename: str,
    format_service: FormatService = Depends(get_format_service)
):
    try:
        output_path = format_service.save_formatted_documents(documents, template, filename)
        return {"output_path": output_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 创建标注任务
@router.post("/create_Tasks")
async def create_task(
    task_data: Dict[str, Any],
    task_service: TaskService = Depends(get_task_service)
):
    try:
        # 创建任务
        task = task_service.create_task(task_data)
        
        # 保存任务
        task_dir = task_service.save_task(task)
        
        return {
            "task_id": task.id,
            "task_dir": task_dir,
            "document_count": len(task.document_ids)
        }
    except ValueError as ve:
        # 处理业务逻辑错误（如格式校验失败）
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        # 处理其他未预期的错误
        print(f"创建任务时出错: {str(e)}")  # 添加日志输出
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")

# 保存标注结果
@router.post("/tasks/{task_id}/annotations/{document_id}")
async def save_annotation(
    task_id: str,
    document_id: str,
    annotation: Dict[str, Any],
    annotator_service: AnnotatorService = Depends(get_annotator_service)
):
    try:
        success = annotator_service.save_annotation(task_id, document_id, annotation)
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"status": "success"}
    except Exception as e:
        print(f"保存标注结果失败: {str(e)}")  # 添加日志输出
        raise HTTPException(status_code=500, detail=str(e))

# 获取标注结果
@router.get("/tasks/{task_id}/annotations/{document_id}")
async def get_annotation(
    task_id: str,
    document_id: str,
    annotator_service: AnnotatorService = Depends(get_annotator_service)
):
    """获取标注结果"""
    try:
        doc = annotator_service.load_annotation(task_id, document_id)
        if (doc is None):
            return {"annotation": {}}
        return {"annotation": doc}  # 返回完整的带标注的文档
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# AI审查
@router.post("/tasks/{task_id}/ai-review")
async def ai_review(
    task_id: str,
    documents: List[Dict[str, Any]],
    prompt_template: str,
    ai_review_service: AIReviewService = Depends(get_ai_review_service)
):
    try:
        results = ai_review_service.batch_review(documents, prompt_template)
        output_path = ai_review_service.save_review_results(task_id, results)
        return {"output_path": output_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 比较AI审查结果与人工标注
@router.get("/tasks/{task_id}/compare")
async def compare_annotations(
    task_id: str,
    ai_review_service: AIReviewService = Depends(get_ai_review_service)
):
    try:
        comparison = ai_review_service.compare_with_human_annotation(task_id)
        return comparison
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 准备训练数据
@router.post("/tasks/{task_id}/prepare-training")
async def prepare_training_data(
    task_id: str,
    train_ratio: float = 0.8,
    training_service: TrainingService = Depends(get_training_service)
):
    try:
        result = training_service.prepare_training_data(task_id, train_ratio)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 上传训练数据
@router.post("/upload-training")
async def upload_training_data(
    training_file: str,
    validation_file: str,
    api_key: str,
    training_service: TrainingService = Depends(get_training_service)
):
    try:
        result = training_service.upload_to_openai(api_key, training_file, validation_file)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 开始训练
@router.post("/start-training")
async def start_training(
    train_file_id: str,
    validation_file_id: str,
    api_key: str,
    training_service: TrainingService = Depends(get_training_service)
):
    try:
        result = training_service.start_training(api_key, train_file_id, validation_file_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 检查训练状态
@router.get("/training-status/{job_id}")
async def check_training_status(
    job_id: str,
    api_key: str,
    training_service: TrainingService = Depends(get_training_service)
):
    try:
        result = training_service.check_training_status(api_key, job_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 获取任务列表
@router.get("/get_Tasks_list")
async def get_tasks(
    task_service: TaskService = Depends(get_task_service)
):
    try:
        tasks = task_service.get_all_tasks()
        return {
            "tasks": [
                {
                    "id": task.id,
                    "name": task.name,
                    "description": task.description,
                    "status": task.status,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat(),
                    "document_count": len(task.document_ids)
                }
                for task in tasks
            ]
        }
    except Exception as e:
        print(f"获取任务列表失败: {str(e)}")  # 添加日志输出
        raise HTTPException(status_code=500, detail=str(e))

# 删除任务
@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: str,
    task_service: TaskService = Depends(get_task_service)
):
    try:
        success = task_service.delete_task(task_id)
        if not success:
            raise HTTPException(status_code=404, detail="任务不存在")
        return {"message": "任务删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 获取任务文档列表
@router.get("/tasks/{task_id}/documents")
async def get_task_documents(
    task_id: str,
    task_service: TaskService = Depends(get_task_service)
):
    try:
        documents = task_service.get_task_documents(task_id)
        return {
            "documents": documents
        }
    except Exception as e:
        print(f"获取任务文档列表失败: {str(e)}")  # 添加日志输出
        raise HTTPException(status_code=500, detail=str(e))

# 获取任务单个文档
@router.get("/tasks/{task_id}/documents/{document_id}")
async def get_task_document(
    task_id: str,
    document_id: str,
    task_service: TaskService = Depends(get_task_service)
):
    try:
        document = task_service.get_task_document(task_id, document_id)
        return {
            "document": document
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 

# 获取任务配置
@router.get("/tasks/{task_id}/config")
async def get_task_config(
    task_id: str,
    task_service: TaskService = Depends(get_task_service)
):
    try:
        task = task_service.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
            
        # 获取模板内容
        template_path = os.path.join(task_service.task_templates_dir, "template_default.json")
        task_config = TaskConfig.from_template(template_path, task.config)
            
        return {
            "status": "success",
            "config": {
                "fields": [
                    {
                        "path": field.path,
                        "name": field.name,
                        "type": field.type,
                        "description": field.description
                    }
                    for field in task_config.fields
                ],
                "beMarked": [field["path"] for field in task.config]  # Add the beMarked field list
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 合并任务标注结果
@router.post("/tasks/{task_id}/merge")
async def merge_task_annotations(
    task_id: str,
    task_service: TaskService = Depends(get_task_service)
):
    try:
        output_path = task_service.merge_annotations(task_id)
        if not output_path:
            raise HTTPException(status_code=400, detail="合并失败或任务未完成标注")
        
        return {
            "message": "合并成功",
            "output_file": output_path,
            "status": "completed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 检查任务完成状态
@router.get("/tasks/{task_id}/completion")
async def check_task_completion(
    task_id: str,
    task_service: TaskService = Depends(get_task_service)
):
    try:
        is_completed = task_service.check_task_completion(task_id)
        return {
            "is_completed": is_completed
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))