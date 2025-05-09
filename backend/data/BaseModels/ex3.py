from pydantic import BaseModel
from typing import Optional

class CriminalCase(BaseModel):
    description: str
    suspect: str
    accusation: str
    range: str
    基准刑_年: int  # 使用中文字段名，注意这在某些IDE中可能有警告
    基准刑_月: int
    
