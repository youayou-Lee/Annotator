#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试模板示例 - 用于验证后端集成
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from enum import Enum

class DocumentType(str, Enum):
    """文档类型枚举"""
    NEWS = "新闻"
    REPORT = "报告"
    ANNOUNCEMENT = "公告"

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

class TestDocumentModel(BaseModel):
    """测试文档主模型"""
    
    # 非标注字段
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
    
    # 嵌套对象标注字段
    author: AuthorInfo = Field(
        ..., 
        json_schema_extra={"is_annotation": True}, 
        description="作者信息"
    )
    
    # 列表标注字段
    tags: List[str] = Field(
        default_factory=list, 
        json_schema_extra={"is_annotation": True}, 
        description="标签列表"
    )
    
    # 非标注字段
    created_at: Optional[str] = Field(default=None, description="创建时间")
    
    # 标识为主模型
    model_config = ConfigDict(
        json_schema_extra={"is_main_model": True},
        populate_by_name=True
    ) 