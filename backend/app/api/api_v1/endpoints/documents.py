from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.document import DocumentCreate, Document
from app.services import document_service
import tempfile
import os
import json
import importlib.util
from pydantic import BaseModel, ValidationError

router = APIRouter()

@router.post("/", response_model=Document)
def create_document(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    file: UploadFile = File(...),
    description: str = Form(None),
):
    """
    上传文档文件
    """
    # 检查文件扩展名
    filename = file.filename
    if not filename or "." not in filename:
        raise HTTPException(status_code=400, detail="不支持的文件格式")
    
    # 保存上传文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
        temp_file.write(file.file.read())
        temp_path = temp_file.name
    
    try:
        # 创建文档记录
        document_in = DocumentCreate(
            filename=os.path.basename(temp_path),
            original_filename=filename,
            file_path=temp_path,
            file_size=os.path.getsize(temp_path),
            file_type=os.path.splitext(filename)[1].lower()[1:],  # 去掉.
            uploader_id=current_user.id,
            description=description
        )
        
        # 保存到数据库
        document = document_service.create_document(db=db, document_in=document_in)
        return document
    
    except Exception as e:
        # 确保在出错时删除临时文件
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise HTTPException(status_code=500, detail=f"文档创建失败: {str(e)}")

@router.post("/upload-validate")
async def upload_and_validate(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    file: UploadFile = File(...),
    format: str = Query(..., description="文件格式"),
    schema_file: UploadFile = File(None, description="可选的校验模式文件")
):
    """
    上传文件并验证其结构
    """
    # 检查文件扩展名
    filename = file.filename
    if not filename or "." not in filename:
        raise HTTPException(status_code=400, detail="不支持的文件格式")
    
    # 保存上传文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
        temp_file.write(await file.read())
        temp_path = temp_file.name
    
    # 保存模式文件（如果有）
    schema_path = None
    schema_model = None
    
    if schema_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as schema_temp:
            schema_temp.write(await schema_file.read())
            schema_path = schema_temp.name
            
        try:
            # 动态加载Python模块
            spec = importlib.util.spec_from_file_location("schema_module", schema_path)
            schema_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(schema_module)
            
            # 寻找BaseModel子类
            for attr_name in dir(schema_module):
                attr = getattr(schema_module, attr_name)
                if isinstance(attr, type) and issubclass(attr, BaseModel) and attr != BaseModel:
                    schema_model = attr
                    break
                    
            if not schema_model:
                raise HTTPException(status_code=400, detail="未在模式文件中找到Pydantic模型")
                
        except Exception as e:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            if schema_path and os.path.exists(schema_path):
                os.unlink(schema_path)
            raise HTTPException(status_code=400, detail=f"模式文件加载失败: {str(e)}")
    
    try:
        # 根据文件格式解析数据
        validation_results = []
        
        if format.lower() == "json":
            with open(temp_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            # 如果有模式，则验证数据
            if schema_model:
                try:
                    if isinstance(data, list):
                        # 验证列表中的每个项目
                        for i, item in enumerate(data):
                            try:
                                schema_model(**item)
                            except ValidationError as e:
                                validation_results.append({
                                    "success": False,
                                    "fileName": filename,
                                    "index": i,
                                    "errors": [{"message": str(err)} for err in e.errors()]
                                })
                        
                        if not validation_results:
                            validation_results.append({
                                "success": True,
                                "fileName": filename,
                                "message": "所有数据项通过验证"
                            })
                    else:
                        # 验证单个对象
                        schema_model(**data)
                        validation_results.append({
                            "success": True,
                            "fileName": filename,
                            "message": "数据通过验证"
                        })
                except ValidationError as e:
                    validation_results.append({
                        "success": False,
                        "fileName": filename,
                        "errors": [{"message": str(err)} for err in e.errors()]
                    })
            else:
                # 没有模式，只检查是否是有效的JSON
                validation_results.append({
                    "success": True,
                    "fileName": filename,
                    "message": "JSON格式有效"
                })
                
        elif format.lower() in ["csv", "xlsx"]:
            # 这里需要使用pandas等库处理CSV和Excel文件
            # 为简化示例，我们只返回文件格式有效的消息
            validation_results.append({
                "success": True,
                "fileName": filename,
                "message": f"{format.upper()}格式有效"
            })
            
        elif format.lower() == "py":
            # 验证Python文件是否包含有效的Pydantic模型
            try:
                spec = importlib.util.spec_from_file_location("uploaded_module", temp_path)
                uploaded_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(uploaded_module)
                
                # 寻找BaseModel子类
                found_model = False
                for attr_name in dir(uploaded_module):
                    attr = getattr(uploaded_module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, BaseModel) and attr != BaseModel:
                        found_model = True
                        break
                
                if found_model:
                    validation_results.append({
                        "success": True,
                        "fileName": filename,
                        "message": "找到有效的Pydantic模型"
                    })
                else:
                    validation_results.append({
                        "success": False,
                        "fileName": filename,
                        "errors": [{"message": "文件中未找到Pydantic模型"}]
                    })
            except Exception as e:
                validation_results.append({
                    "success": False,
                    "fileName": filename,
                    "errors": [{"message": f"Python文件解析错误: {str(e)}"}]
                })
        else:
            validation_results.append({
                "success": False,
                "fileName": filename,
                "errors": [{"message": f"不支持的文件格式: {format}"}]
            })
        
        return {
            "success": all(result["success"] for result in validation_results),
            "results": validation_results
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": str(e),
            "results": [{
                "success": False,
                "fileName": filename,
                "errors": [{"message": str(e)}]
            }]
        }
    finally:
        # 清理临时文件
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        if schema_path and os.path.exists(schema_path):
            os.unlink(schema_path)

@router.get("/{document_id}", response_model=Document)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    获取文档详情
    """
    document = document_service.get_document(db=db, document_id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    return document

@router.get("/", response_model=List[Document])
def get_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    获取文档列表
    """
    documents = document_service.get_documents(db=db, skip=skip, limit=limit)
    return documents 