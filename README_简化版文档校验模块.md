# 简化版文档校验模块

## 概述

这是一个基于 Pydantic v2 的轻量级文档校验模块，保留了原始复杂版本的核心功能，但代码更简洁易懂。主要用于验证 JSON/JSONL 文档是否符合预定义的模板结构，并提取标注字段。

## 核心功能

### ✅ 已实现的功能

1. **模板验证**
   - Python 语法检查
   - 主模型自动识别
   - BaseModel 结构验证

2. **文档验证**
   - 单个文档验证
   - JSON/JSONL 文件批量验证
   - 详细错误信息

3. **标注字段处理**
   - 递归提取标注字段
   - 支持嵌套结构和列表
   - 约束条件提取

4. **数据提取**
   - 从验证后的文档提取标注字段值
   - 支持复杂嵌套路径
   - 防止循环引用

## 文件结构

```
简化版文档校验模块/
├── simple_document_validator.py    # 核心验证器
├── simple_template_example.py      # 模板示例
├── test_sample_data.json          # 测试数据
├── test_simple_validator.py       # 完整测试脚本
└── README_简化版文档校验模块.md    # 本文档
```

## 快速开始

### 1. 环境要求

```bash
# 确保处于正确的 conda 环境
conda activate annotator

# 安装依赖
pip install pydantic>=2.0.0
```

### 2. 基本使用

```python
from simple_document_validator import SimpleDocumentValidator

# 创建验证器
validator = SimpleDocumentValidator()

# 加载模板
result = validator.load_template("simple_template_example.py")
if result["valid"]:
    print("✅ 模板加载成功")
    
    # 验证文档
    doc_result = validator.validate_document(your_json_data)
    if doc_result["valid"]:
        # 提取标注字段
        annotations = validator.extract_annotations(your_json_data)
        print("提取的标注字段:", annotations)
```

### 3. 运行测试

```bash
# 运行完整测试
python test_simple_validator.py
```

## 模板格式

### 基本模板结构

```python
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

class YourModel(BaseModel):
    # 非标注字段（仅用于验证）
    id: str = Field(..., description="文档ID")
    
    # 标注字段（会被提取）
    title: str = Field(
        ..., 
        json_schema_extra={"is_annotation": True}, 
        min_length=5, 
        max_length=200,
        description="文档标题"
    )
    
    # 标识为主模型
    model_config = ConfigDict(
        json_schema_extra={"is_main_model": True}
    )
```

### 关键标记

1. **主模型标识**：
   ```python
   model_config = ConfigDict(json_schema_extra={"is_main_model": True})
   ```

2. **标注字段标记**：
   ```python
   field_name: str = Field(..., json_schema_extra={"is_annotation": True})
   ```

## 支持的字段类型

### 基础类型
- `str`：字符串
- `int`：整数
- `float`：浮点数
- `bool`：布尔值
- `List[str]`：字符串列表

### 复杂类型
- `BaseModel`：嵌套对象
- `List[BaseModel]`：对象列表
- `Optional[Type]`：可选字段
- `Enum`：枚举类型

### 约束条件
- `min_length`、`max_length`：字符串长度
- `ge`、`le`、`gt`、`lt`：数值范围
- `regex`：正则表达式

## 路径表示法

验证器使用清晰的路径来标识嵌套字段：

- 基础字段：`title`
- 嵌套对象：`author.name`
- 数组元素：`paragraphs[].content`
- 深层嵌套：`sections[].subsections[].title`

## API 参考

### SimpleDocumentValidator

#### 主要方法

```python
# 加载模板
load_template(template_path: str) -> Dict[str, Any]

# 验证单个文档
validate_document(data: dict) -> Dict[str, Any]

# 验证文件
validate_file(file_path: str) -> Dict[str, Any]

# 提取标注字段
extract_annotations(data: dict) -> Dict[str, Any]

# 获取字段模式
get_annotation_schema() -> List[Dict[str, Any]]
```

#### 返回格式

**成功验证**：
```python
{
    "valid": True,
    "instance": <pydantic_instance>
}
```

**验证失败**：
```python
{
    "valid": False,
    "errors": [
        {
            "loc": ["field_name"],
            "msg": "错误信息",
            "type": "错误类型"
        }
    ]
}
```

## 使用示例

### 完整示例

```python
from simple_document_validator import SimpleDocumentValidator

# 1. 初始化
validator = SimpleDocumentValidator("simple_template_example.py")

# 2. 验证文档
document = {
    "id": "doc_001",
    "title": "测试文档标题",
    "document_type": "报告",
    "author": {
        "name": "张三",
        "affiliation": "测试机构"
    },
    "paragraphs": [
        {
            "content": "这是段落内容，需要满足最小长度要求。",
            "page_number": 1,
            "keywords": ["测试", "内容"]
        }
    ],
    "tags": ["测试", "示例"]
}

# 3. 执行验证
result = validator.validate_document(document)
if result["valid"]:
    print("✅ 文档验证通过")
    
    # 4. 提取标注字段
    annotations = validator.extract_annotations(document)
    for path, value in annotations.items():
        print(f"{path}: {value}")
else:
    print("❌ 文档验证失败")
    for error in result["errors"]:
        print(f"错误: {error}")
```

