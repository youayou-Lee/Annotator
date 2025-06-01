from typing import List, Dict, Any, Optional, Union, Literal
from pydantic import BaseModel, Field
from enum import Enum

class NewsCategory(str, Enum):
    POLITICS = "政治"
    ECONOMY = "经济"
    TECHNOLOGY = "科技"
    SPORTS = "体育"
    ENTERTAINMENT = "娱乐"
    HEALTH = "健康"
    EDUCATION = "教育"
    SOCIETY = "社会"
    INTERNATIONAL = "国际"
    OTHER = "其他"

class SentimentType(str, Enum):
    POSITIVE = "正面"
    NEGATIVE = "负面"
    NEUTRAL = "中性"

class EntityType(str, Enum):
    PERSON = "人物"
    ORGANIZATION = "组织"
    LOCATION = "地点"
    PRODUCT = "产品"
    TECHNOLOGY = "技术"
    OTHER = "其他"

class EntityInfo(BaseModel):
    name: str = Field(description="实体名称", example="某知名科技公司")
    entity_type: EntityType = Field(
        description="实体类型",
        example=EntityType.ORGANIZATION
    )
    start_pos: int = Field(description="在文本中的起始位置", ge=0, example=10)
    end_pos: int = Field(description="在文本中的结束位置", ge=0, example=20)
    confidence: float = Field(description="识别置信度", ge=0.0, le=1.0, example=0.95)

class KeywordInfo(BaseModel):
    keyword: str = Field(description="关键词", example="人工智能")
    importance: int = Field(description="重要性评分", ge=1, le=5, example=5)
    frequency: int = Field(description="在文本中出现频次", ge=1, example=3)

class AnnotationSchema:
    schema_name = "新闻文章标注模板"
    version = "1.0.0"
    description = "用于新闻文章内容分析和标注的模板，包含分类、情感分析、关键信息提取等功能"
    
    class Fields(BaseModel):
        # 基本信息标注
        article_title: str = Field(
            description="文章标题",
            min_length=1,
            max_length=200,
            example="人工智能技术在医疗领域的最新突破"
        )
        
        article_summary: str = Field(
            description="文章摘要（100-300字）",
            min_length=50,
            max_length=500,
            ui_widget="textarea",
            example="本文报道了某科技公司发布的AI医疗诊断系统，该系统通过深度学习算法分析医学影像，能够准确识别早期癌症病变。"
        )
        
        # 分类标注
        primary_category: NewsCategory = Field(
            description="主要分类",
            example=NewsCategory.TECHNOLOGY
        )
        
        secondary_categories: List[NewsCategory] = Field(
            description="次要分类（可多选）",
            default=[],
            example=[NewsCategory.HEALTH]
        )
        
        # 情感分析
        overall_sentiment: SentimentType = Field(
            description="整体情感倾向",
            example=SentimentType.POSITIVE
        )
        
        sentiment_confidence: float = Field(
            description="情感分析置信度",
            ge=0.0,
            le=1.0,
            example=0.85
        )
        
        # 内容质量评估
        content_quality: int = Field(
            description="内容质量评分",
            ge=1,
            le=5,
            example=4
        )
        
        factual_accuracy: int = Field(
            description="事实准确性评分",
            ge=1,
            le=5,
            example=5
        )
        
        readability: int = Field(
            description="可读性评分",
            ge=1,
            le=5,
            example=4
        )
        
        # 关键信息提取
        main_entities: List[EntityInfo] = Field(
            description="主要实体信息",
            default=[],
            example=[{
                "name": "某知名科技公司",
                "entity_type": "组织",
                "start_pos": 10,
                "end_pos": 18,
                "confidence": 0.95
            }]
        )
        
        keywords: List[KeywordInfo] = Field(
            description="关键词信息",
            default=[],
            example=[{
                "keyword": "人工智能",
                "importance": 5,
                "frequency": 3
            }]
        )
        
        # 事实核查
        contains_statistics: bool = Field(
            description="是否包含统计数据",
            example=True
        )
        
        statistics_verified: Optional[bool] = Field(
            description="统计数据是否已验证",
            depends_on={"contains_statistics": True},
            default=None,
            example=True
        )
        
        source_credibility: int = Field(
            description="信息源可信度",
            ge=1,
            le=5,
            example=4
        )
        
        # 标注元信息
        annotation_notes: Optional[str] = Field(
            description="标注备注",
            ui_widget="textarea",
            default="",
            example="文章内容客观，数据来源可靠，适合推荐。"
        )
        
        annotation_difficulty: int = Field(
            description="标注难度",
            ge=1,
            le=5,
            example=2
        )
        
        requires_expert_review: bool = Field(
            description="是否需要专家复审",
            example=False
        )
    
    fields = Fields 