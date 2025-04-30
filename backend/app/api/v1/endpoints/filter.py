from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.services.filter_service import FilterService
from app.schemas.filter import FilterCriteria, FilterOptions

router = APIRouter()

@router.post("/filter", response_model=List[Dict[str, Any]])
def filter_documents(
    filter_criteria: FilterCriteria,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
):
    """
    根据过滤条件筛选文书
    """
    try:
        filter_service = FilterService(db)
        documents = filter_service.filter_documents(filter_criteria.dict())
        return [doc.__dict__ for doc in documents]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/filter-options", response_model=FilterOptions)
def get_filter_options(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
):
    """
    获取可用的过滤选项
    """
    try:
        filter_service = FilterService(db)
        return filter_service.get_filter_options()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 