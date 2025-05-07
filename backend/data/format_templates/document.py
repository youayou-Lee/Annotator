from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field



class LegalBasis(BaseModel):
    """法定刑裁判依据"""
    罪名: str
    构成要件判断: str

class MainPunishment(BaseModel):
    """主刑"""
    管制: Optional[int] = None
    拘役: Optional[int] = None
    有期徒刑: Optional[int] = None
    无期徒刑: Optional[bool] = None
    死刑: Optional[bool] = None

class AdditionalPunishment(BaseModel):
    """附加刑"""
    罚金: Optional[int] = None
    剥夺政治权利: Optional[bool] = None
    没收财产: Optional[str] = None
    驱逐出境: Optional[bool] = None

class JudgmentResult(BaseModel):
    """裁判结果"""
    主刑: MainPunishment
    附加刑: AdditionalPunishment
    是否缓刑: bool
    第一层面量刑调节要素: List[str]
    第二层面量刑调节要素: List[str]
    法定刑区间: str
    与宣告刑是否一致: bool

class JudgmentDetail(BaseModel):
    """裁判详情模型"""
    被告人姓名: str
    法定刑裁判依据: LegalBasis
    裁判结果: JudgmentResult

class Document(BaseModel):
    """文书模型"""
    id: str
    当事人: List[str]
    裁判文书名: str
    案件经过: str
    s25: str
    s26: str
    s27: str
    裁判详情: List[JudgmentDetail]