# 增强文档验证器

这是一个基于Pydantic v2的文档验证器，支持复杂嵌套结构的JSON文档验证和标注字段提取。

## 主要功能

### 1. 多层嵌套结构支持
- 支持任意深度的BaseModel嵌套
- 支持List[BaseModel]类型的数组嵌套
- 支持Optional[BaseModel]类型的可选嵌套
- 自动处理循环引用，防止无限递归

### 2. 主模型自动识别
- 使用`model_config`中的`json_schema_extra={"is_main_model": True}`标识主模型
- 支持多BaseModel文件中的主模型自动选择
- 当只有一个BaseModel时自动选择为主模型

### 3. 标注字段灵活标记
- 使用`json_schema_extra={"is_annotation": True}`标记需要标注的字段
- 支持基础类型、嵌套模型、数组等各种字段类型的标注
- 自动提取字段类型、约束条件和描述信息

### 4. 约束条件完整支持
- 支持数值约束：`ge`, `le`, `gt`, `lt`
- 支持字符串约束：`min_length`, `max_length`, `pattern`
- 支持其他约束：`multiple_of`等
- 完全基于Pydantic v2的metadata约束系统

## 系统要求

- Python 3.8+
- Pydantic v2.0+

## 文件结构

```
document_validator/
├── enhanced_validator.py      # 增强的验证器核心代码
├── complex_template.py        # 复杂嵌套模板示例
├── complex_sample.json        # 复杂示例数据
├── test_enhanced_validator.py # 完整测试套件
├── usage_example.py           # 使用示例
└── README.md                  # 本文档
```

## 快速开始

### 1. 创建模板文件

```python
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

class NestedModel(BaseModel):
    """嵌套模型"""
    field1: str = Field(..., json_schema_extra={"is_annotation": True}, description="字段1")
    field2: float = Field(..., json_schema_extra={"is_annotation": True}, ge=0.0, le=1.0, description="字段2")

class MainModel(BaseModel):
    """主模型"""
    id: str = Field(..., description="文档ID")
    text: str = Field(..., json_schema_extra={"is_annotation": True}, description="主要文本")
    nested: NestedModel = Field(..., json_schema_extra={"is_annotation": True}, description="嵌套对象")
    items: List[NestedModel] = Field(..., json_schema_extra={"is_annotation": True}, description="嵌套数组")
    
    model_config = ConfigDict(
        json_schema_extra={"is_main_model": True}  # 标识主模型
    )
```

### 2. 使用验证器

```python
from enhanced_validator import EnhancedDocumentValidator

# 初始化验证器
validator = EnhancedDocumentValidator("your_template.py")

# 验证文档
result = validator.validate_document(your_json_data)
if result["valid"]:
    print("验证通过")
else:
    print("验证失败:", result["errors"])

# 提取标注字段
annotations = validator.extract_annotations(your_json_data)
for path, value in annotations.items():
    print(f"{path}: {value}")

# 获取标注字段模式
schema = validator.get_annotation_schema()
for field in schema:
    print(f"路径: {field['path']}")
    print(f"类型: {field['type']}")
    print(f"约束: {field['constraints']}")
```

## 核心特性详解

### 1. 路径表示法

验证器使用清晰的路径表示法来标识嵌套字段：

- 基础字段：`field_name`
- 嵌套对象：`parent.child`
- 数组元素：`array_field[]`
- 深层嵌套：`parent.array[].nested.field`

### 2. 约束提取

自动从Pydantic v2 Field中提取约束条件：

```python
# 数值约束
score: float = Field(..., ge=-1.0, le=1.0)  # 提取: {'ge': -1.0, 'le': 1.0}

# 字符串约束
title: str = Field(..., min_length=5, max_length=200)  # 提取: {'min_length': 5, 'max_length': 200}
```

### 3. 复杂嵌套处理

支持任意复杂的嵌套结构：

```python
class Level3(BaseModel):
    field: str = Field(..., json_schema_extra={"is_annotation": True})

class Level2(BaseModel):
    level3_list: List[Level3] = Field(..., json_schema_extra={"is_annotation": True})

class Level1(BaseModel):
    level2: Level2 = Field(..., json_schema_extra={"is_annotation": True})

class MainModel(BaseModel):
    level1_array: List[Level1] = Field(..., json_schema_extra={"is_annotation": True})
    
    model_config = ConfigDict(json_schema_extra={"is_main_model": True})
```

提取路径：`level1_array[].level2.level3_list[].field`

## 测试

运行完整测试套件：

```bash
python test_enhanced_validator.py
```

运行使用示例：

```bash
python usage_example.py
```

