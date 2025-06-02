from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

class AnalysisInfo(BaseModel):
    """分析信息模型 - 深层嵌套"""
    topic: str = Field(..., json_schema_extra={"is_annotation": True}, description="主题分类")
    confidence: float = Field(..., json_schema_extra={"is_annotation": True}, ge=0.0, le=1.0, description="置信度")
    
class SubsectionModel(BaseModel):
    """子章节模型"""
    subsection_id: str
    content: str = Field(..., json_schema_extra={"is_annotation": True}, description="子章节内容")
    analysis: AnalysisInfo = Field(..., json_schema_extra={"is_annotation": True}, description="分析信息")

class AnnotationInfo(BaseModel):
    """标注信息模型 - 嵌套模型"""
    sentiment_score: float = Field(..., json_schema_extra={"is_annotation": True}, ge=-1.0, le=1.0, description="情感分数")
    key_entities: List[str] = Field(..., json_schema_extra={"is_annotation": True}, description="关键实体")
    importance_level: int = Field(..., json_schema_extra={"is_annotation": True}, ge=1, le=5, description="重要性等级")

class ContentSection(BaseModel):
    """内容章节模型"""
    section_id: str
    text: str = Field(..., json_schema_extra={"is_annotation": True}, description="章节文本")
    annotations: AnnotationInfo = Field(..., json_schema_extra={"is_annotation": True}, description="标注信息")
    subsections: Optional[List[SubsectionModel]] = Field(default=None, json_schema_extra={"is_annotation": True}, description="子章节列表")

class DocumentMetadata(BaseModel):
    """文档元数据模型"""
    author: str = Field(..., json_schema_extra={"is_annotation": True}, description="作者")
    publish_date: str = Field(..., json_schema_extra={"is_annotation": True}, description="发布日期")
    classification: str = Field(..., json_schema_extra={"is_annotation": True}, description="分类级别")

class DocumentInfo(BaseModel):
    """文档信息模型"""
    title: str = Field(..., json_schema_extra={"is_annotation": True}, min_length=5, max_length=200, description="文档标题")
    category: str = Field(..., json_schema_extra={"is_annotation": True}, description="文档类别")
    metadata: DocumentMetadata = Field(..., json_schema_extra={"is_annotation": True}, description="元数据")

class StatisticsInfo(BaseModel):
    """统计信息模型 - 非主模型"""
    word_count: int = Field(..., ge=0)
    paragraph_count: int = Field(..., ge=0)
    reading_time: int = Field(..., ge=0)

# 这是一个辅助模型，不是主模型
class AuxiliaryModel(BaseModel):
    """辅助模型 - 用于测试多BaseModel情况"""
    aux_id: str
    aux_data: str
    
    model_config = ConfigDict(
        json_schema_extra={"is_main_model": False}  # 明确标识这不是主模型
    )

class ComplexDocumentModel(BaseModel):
    """复杂文档主模型 - 处理多层嵌套"""
    id: str = Field(..., description="文档ID")
    text1: str = Field(..., json_schema_extra={"is_annotation": True}, description="主要文本内容")
    end: int = Field(..., json_schema_extra={"is_annotation": True}, ge=0, description="结束位置")
    document_info: DocumentInfo = Field(..., json_schema_extra={"is_annotation": True}, description="文档信息")
    content_sections: List[ContentSection] = Field(..., json_schema_extra={"is_annotation": True}, description="内容章节")
    statistics: StatisticsInfo = Field(..., description="统计信息（非标注字段）")
    
    model_config = ConfigDict(
        json_schema_extra={"is_main_model": True},  # 标识这是主模型
        populate_by_name=True
    )