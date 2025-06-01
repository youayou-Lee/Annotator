"""
测试标注模板
定义文档标注的字段和验证规则
"""

ANNOTATION_FIELDS = {
    "title": {
        "type": "string",
        "required": True,
        "description": "文档标题"
    },
    "category": {
        "type": "string",
        "required": True,
        "options": ["新闻", "公告", "报告"],
        "description": "文档分类"
    },
    "keywords": {
        "type": "array",
        "required": False,
        "description": "关键词列表"
    },
    "summary": {
        "type": "string",
        "required": False,
        "description": "文档摘要"
    }
}

def validate_annotation(data):
    """验证标注数据"""
    for field, config in ANNOTATION_FIELDS.items():
        if config.get("required", False) and field not in data:
            return False, f"缺少必填字段: {field}"
    return True, "验证通过"
