from pydantic import BaseModel
from typing import List
class Label(BaseModel):
    嫌疑人: List[str]
    被告人: List[str]
    类型: str
    摘要: str