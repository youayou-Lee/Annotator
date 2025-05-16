from typing import Any, List, Dict
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse, JSONResponse
import os
import json
import shutil
from pathlib import Path

router = APIRouter()

# 获取项目根目录（假设backend是根目录的直接子目录）
ROOT_DIR = Path(os.path.abspath(__file__)).parent.parent.parent.parent.parent.parent
# 公共文件目录路径，使用绝对路径
PUBLIC_DIR = ROOT_DIR / "data" / "public"
DOCUMENTS_DIR = PUBLIC_DIR / "documents"
TEMPLATES_DIR = PUBLIC_DIR / "templates"
SCHEMAS_DIR = PUBLIC_DIR / "schemas"
EXPORTS_DIR = PUBLIC_DIR / "exports"

# 调试信息
print(f"根目录: {ROOT_DIR}")
print(f"公共目录: {PUBLIC_DIR}")
print(f"文档目录: {DOCUMENTS_DIR}")
print(f"模板目录: {TEMPLATES_DIR}")
print(f"模式目录: {SCHEMAS_DIR}")
print(f"导出目录: {EXPORTS_DIR}")

# 确保目录存在
for dir_path in [PUBLIC_DIR, DOCUMENTS_DIR, TEMPLATES_DIR, SCHEMAS_DIR, EXPORTS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

@router.get("/files", response_model=Dict[str, List[Dict[str, Any]]])
def list_public_files():
    """
    列出所有公共文件，按类型分组
    """
    result = {
        "documents": [],
        "templates": [],
        "schemas": [],
        "exports": []
    }
    
    # 获取文档文件
    for file_path in DOCUMENTS_DIR.glob("*"):
        if file_path.is_file():
            result["documents"].append({
                "name": file_path.name,
                "path": str(file_path.relative_to(PUBLIC_DIR)),
                "size": file_path.stat().st_size,
                "modified": file_path.stat().st_mtime
            })
    
    # 获取模板文件
    for file_path in TEMPLATES_DIR.glob("*"):
        if file_path.is_file():
            result["templates"].append({
                "name": file_path.name,
                "path": str(file_path.relative_to(PUBLIC_DIR)),
                "size": file_path.stat().st_size,
                "modified": file_path.stat().st_mtime
            })
    
    # 获取模式文件
    for file_path in SCHEMAS_DIR.glob("*"):
        if file_path.is_file():
            result["schemas"].append({
                "name": file_path.name,
                "path": str(file_path.relative_to(PUBLIC_DIR)),
                "size": file_path.stat().st_size,
                "modified": file_path.stat().st_mtime
            })
    
    # 获取导出文件
    for file_path in EXPORTS_DIR.glob("*"):
        if file_path.is_file():
            result["exports"].append({
                "name": file_path.name,
                "path": str(file_path.relative_to(PUBLIC_DIR)),
                "size": file_path.stat().st_size,
                "modified": file_path.stat().st_mtime
            })
    
    return result

@router.get("/download/{file_type}/{file_name}")
def download_public_file(file_type: str, file_name: str):
    """
    下载公共文件
    """
    if file_type not in ["documents", "templates", "schemas", "exports"]:
        raise HTTPException(status_code=400, detail="不支持的文件类型")
    
    file_path = PUBLIC_DIR / file_type / file_name
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        path=str(file_path),
        filename=file_name,
        media_type="application/octet-stream"
    )

@router.post("/upload/{file_type}")
async def upload_public_file(
    file_type: str,
    file: UploadFile = File(...),
    description: str = Form(None)
):
    """
    上传文件到公共目录
    """
    if file_type not in ["documents", "templates", "schemas", "exports"]:
        raise HTTPException(status_code=400, detail="不支持的文件类型")
    
    # 检查文件扩展名
    file_name = file.filename
    if not file_name:
        raise HTTPException(status_code=400, detail="无效的文件名")
    
    # 目标目录和文件路径
    target_dir = PUBLIC_DIR / file_type
    file_path = target_dir / file_name
    
    try:
        # 保存上传的文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return {
            "success": True,
            "message": "文件上传成功",
            "file": {
                "name": file_name,
                "path": str(file_path.relative_to(PUBLIC_DIR)),
                "size": file_path.stat().st_size,
                "modified": file_path.stat().st_mtime,
                "description": description
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

@router.delete("/delete/{file_type}/{file_name}")
def delete_public_file(file_type: str, file_name: str):
    """
    删除公共文件
    """
    if file_type not in ["documents", "templates", "schemas", "exports"]:
        raise HTTPException(status_code=400, detail="不支持的文件类型")
    
    file_path = PUBLIC_DIR / file_type / file_name
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    try:
        os.remove(file_path)
        return {"success": True, "message": "文件删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件删除失败: {str(e)}")

@router.get("/preview/{file_type}/{file_name}")
def preview_public_file(file_type: str, file_name: str):
    """
    预览公共文件内容
    """
    if file_type not in ["documents", "templates", "schemas", "exports"]:
        raise HTTPException(status_code=400, detail="不支持的文件类型")
    
    file_path = PUBLIC_DIR / file_type / file_name
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    try:
        # 对于JSON文件，返回解析后的内容
        if file_path.suffix.lower() == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            return content
        
        # 对于Python文件，返回文本内容
        elif file_path.suffix.lower() == '.py':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {"content": content}
        
        # 对于其他文件，返回错误
        else:
            raise HTTPException(status_code=400, detail="不支持的文件格式预览")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="无效的JSON文件")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件预览失败: {str(e)}") 