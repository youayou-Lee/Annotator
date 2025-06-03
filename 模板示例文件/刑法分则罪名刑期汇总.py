from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class RangeItem(BaseModel):
    main_range: str
    additional: str
    harm_degree: Optional[str] = ""  # 允许为空字符串

class CriminalLawArticle(BaseModel):
    id: str = Field(
        ..., 
        json_schema_extra={"is_annotation": True}, 
        min_length=2, 
        max_length=50,
        description="作者姓名"
    )
    criminal_names: List[str]
    criminal_names_expr: List[str]  # 允许空字符串列表
    description: str = Field(
        ..., 
        json_schema_extra={"is_annotation": True}, 
        min_length=2, 
        max_length=50,
        description="作者姓名"
    )
    range: List[RangeItem]
    # 标识为主模型
    model_config = ConfigDict(
        json_schema_extra={"is_main_model": True},
        populate_by_name=True
    )
