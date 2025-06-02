#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单文档模板示例
演示基本的标注字段定义和嵌套结构
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from enum import Enum

class DocumentType(str, Enum):
    """文档类型枚举"""
    NEWS = "新闻"
    REPORT = "报告"
    ANNOUNCEMENT = "公告"
    RESEARCH = "研究"

class AuthorInfo(BaseModel):
    """作者信息模型"""
    name: str = Field(
        ..., 
        json_schema_extra={"is_annotation": True}, 
        min_length=2, 
        max_length=50,
        description="作者姓名"
    )
    
    affiliation: str = Field(
        ..., 
        json_schema_extra={"is_annotation": True}, 
        description="所属机构"
    )
    
    email: Optional[str] = Field(
        default=None, 
        json_schema_extra={"is_annotation": True}, 
        description="联系邮箱"
    )

class ParagraphInfo(BaseModel):
    """段落信息模型"""
    content: str = Field(
        ..., 
        json_schema_extra={"is_annotation": True}, 
        min_length=10,
        description="段落内容"
    )
    
    page_number: int = Field(
        ..., 
        json_schema_extra={"is_annotation": True}, 
        ge=1,
        description="页码"
    )
    
    sentiment_score: Optional[float] = Field(
        default=None, 
        json_schema_extra={"is_annotation": True}, 
        ge=-1.0, 
        le=1.0,
        description="情感分数"
    )
    
    keywords: List[str] = Field(
        default_factory=list, 
        json_schema_extra={"is_annotation": True}, 
        description="关键词列表"
    )

class SimpleDocumentModel(BaseModel):
    """简单文档主模型"""
    
    # 非标注字段（用于验证但不提取）
    id: str = Field(..., description="文档唯一标识")
    
    # 基础标注字段
    title: str = Field(
        ..., 
        json_schema_extra={"is_annotation": True}, 
        min_length=5, 
        max_length=200,
        description="文档标题"
    )
    
    document_type: DocumentType = Field(
        ..., 
        json_schema_extra={"is_annotation": True}, 
        description="文档类型"
    )
    
    summary: Optional[str] = Field(
        default=None, 
        json_schema_extra={"is_annotation": True}, 
        max_length=500,
        description="文档摘要"
    )
    
    # 嵌套对象标注字段
    author: AuthorInfo = Field(
        ..., 
        json_schema_extra={"is_annotation": True}, 
        description="作者信息"
    )
    
    # 列表标注字段
    paragraphs: List[ParagraphInfo] = Field(
        ..., 
        json_schema_extra={"is_annotation": True}, 
        min_length=1,
        description="段落列表"
    )
    
    tags: List[str] = Field(
        default_factory=list, 
        json_schema_extra={"is_annotation": True}, 
        description="标签列表"
    )
    
    # 非标注字段
    created_at: Optional[str] = Field(default=None, description="创建时间")
    word_count: Optional[int] = Field(default=None, ge=0, description="字数统计")
    
    # 标识为主模型
    model_config = ConfigDict(
        json_schema_extra={"is_main_model": True},
        populate_by_name=True
    ) 