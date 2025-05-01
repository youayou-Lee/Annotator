from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.services.filter_service import FilterService
from app.schemas.filter import FilterCriteria, FilterOptions

router = APIRouter()

@router.post("/filter")
async def filter_documents(
    file_names: List[str],
    filter_conditions: Dict[str, Any]
) -> Dict[str, Any]:
    """
    根据过滤条件筛选文书文件
    
    Args:
        file_names: 要处理的文件名列表
        filter_conditions: 过滤条件
    
    Returns:
        包含过滤结果的字典
    """
    try:
        filter_service = FilterService()
        
        # 加载并过滤文档
        filtered_docs = filter_service.load_and_filter_documents(file_names, filter_conditions)
        
        # 保存过滤结果
        output_file = f"filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        output_path = filter_service.save_filtered_documents(filtered_docs, output_file)
        
        return {
            "message": "过滤完成",
            "output_file": output_file,
            "document_count": len(filtered_docs),
            "output_path": output_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files")
async def get_available_files() -> Dict[str, List[str]]:
    """获取可用的文书文件列表"""
    try:
        filter_service = FilterService()
        files = filter_service.get_available_files()
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))