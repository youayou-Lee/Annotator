from pydantic import BaseModel, Field, field_validator
import re
from typing import List
guided_regex = "(辨认笔录|鉴定意见|勘验、检查、侦查实验等笔录|视听资料、电子数据|书证|以上都不是|被害人陈述|犯罪嫌疑人供述与辩解|证人证言)$"
class Label(BaseModel):
    嫌疑人: List[str]
    被告人: List[str]
    类型: str
    摘要: str
    @field_validator("类型")
    def validate_type(cls, value):
        if not re.match(guided_regex, value):
            raise ValueError(f"类型 must match the pattern: {guided_regex}")
        return value
