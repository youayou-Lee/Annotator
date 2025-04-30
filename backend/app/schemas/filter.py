from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class DateRange(BaseModel):
    start: Optional[datetime] = None
    end: Optional[datetime] = None

class FilterCriteria(BaseModel):
    """过滤条件模型"""
    court: Optional[str] = None
    case_type: Optional[str] = None
    date_range: Optional[DateRange] = None
    content_filters: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    is_annotated: Optional[bool] = None
    is_ai_reviewed: Optional[bool] = None

class FilterOptions(BaseModel):
    """过滤选项模型"""
    courts: List[str]
    case_types: List[str]
    statuses: List[str]
    date_ranges: Dict[str, datetime] 