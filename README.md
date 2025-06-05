# 文书标注系统

一个基于 React + FastAPI 构建的现代化文书标注系统，支持文档上传、任务分配、标注工作和复审流程。

## 系统架构

- **前端**: React 18 + TypeScript + Ant Design + Vite
- **后端**: Python FastAPI + Pydantic
- **存储**: 文件系统（JSON格式）
- **状态管理**: Zustand
- **HTTP客户端**: Axios + React Query

## 功能特性

### ✅ 已完成功能
- 项目基础架构搭建
- 前端React应用框架
- 用户认证系统
- 响应式布局设计
- 路由系统配置
- API服务层封装
- 状态管理实现

### 🔄 开发中功能
- 文件上传与管理
- 任务创建与分配
- 动态表单生成
- 文档标注功能
- 复审与审批流程
- 数据导出功能
- 用户权限管理

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- Conda (推荐)

### 1. 克隆项目
```bash
git clone <repository-url>
cd annotation-system
```

### 2. 安装依赖

#### 后端依赖
```bash
# 创建conda环境
conda create -n annotator python=3.8
conda activate annotator

# 安装Python依赖
cd backend
pip install -r requirements.txt
```

#### 前端依赖
```bash
cd frontend
npm install
```

### 3. 启动开发服务器

#### 方式一：分别启动
```bash
# 启动后端 (终端1)
cd backend
conda activate annotator
uvicorn app.main:app --reload --port 8000

# 启动前端 (终端2)
cd frontend
npm run dev
```

#### 方式二：同时启动
```bash
# 在项目根目录
npm run dev
```

### 4. 访问应用
- 前端应用: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 项目结构

```
annotation-system/
├── frontend/                   # React前端应用
│   ├── src/
│   │   ├── components/        # 公共组件
│   │   ├── pages/            # 页面组件
│   │   ├── router/           # 路由配置
│   │   ├── services/         # API服务
│   │   ├── stores/           # 状态管理
│   │   └── types/            # TypeScript类型
│   ├── package.json
│   └── vite.config.ts
├── backend/                   # FastAPI后端应用
│   ├── app/
│   │   ├── api/              # API路由
│   │   ├── core/             # 核心配置
│   │   └── models/           # 数据模型
│   ├── data/                 # 数据存储
│   └── requirements.txt
├── docs/                     # 项目文档
├── package.json              # 项目配置
└── README.md
```

## 用户角色

系统支持三种用户角色：

- **super_admin**: 超级管理员，拥有所有权限
- **admin**: 管理员，可管理用户和任务
- **annotator**: 标注员，只能进行标注工作

## 主要功能模块

### 1. 用户认证
- 登录/注册
- 权限控制
- 会话管理

### 2. 文件管理
- 文档上传（JSON/JSONL）
- 模板上传（Python）
- 文件预览和下载

### 3. 任务管理
- 任务创建和分配
- 进度跟踪
- 状态管理

### 4. 标注功能
- 动态表单生成
- 实时保存
- 数据验证

### 5. 复审流程
- 标注结果审核
- 修改历史记录
- 质量控制

### 6. 数据导出
- 多格式导出（JSON/CSV/Excel）
- 批量处理
- 数据统计

## 开发指南

### 前端开发
```bash
cd frontend
npm run dev          # 启动开发服务器
npm run build        # 构建生产版本
npm run preview      # 预览生产版本
```

### 后端开发
```bash
cd backend
conda activate annotator
uvicorn app.main:app --reload  # 启动开发服务器
```

### 代码规范
- 前端使用 TypeScript + ESLint
- 后端使用 Python + Black + isort
- 提交前请运行代码检查

## 部署

### 开发环境
```bash
npm run dev
```

### 生产环境
```bash
# 构建前端
npm run build

# 部署后端
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API文档

启动后端服务后，访问以下地址查看API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

如有问题或建议，请通过以下方式联系：
- 创建 Issue
- 发送邮件到 [your-email@example.com]

## 更新日志

### v1.0.0 (2024-01-01)
- ✅ 完成项目基础架构
- ✅ 实现前端React应用框架
- ✅ 完成用户认证系统
- ✅ 实现响应式布局设计
- 🔄 开发中：文件管理功能
- 🔄 开发中：任务管理功能

## 前端表单校验优化

### 问题描述
原先前端标注页面对表单字段进行过于严格的类型校验，导致除了字符串类型外的字段无法正常填写。

### 解决方案
1. **简化前端校验**：前端现在只进行基本的必填项检查
2. **后端校验**：复杂的数据校验（类型、约束、格式等）交由后端处理
3. **错误回显**：保存时如果有校验错误，后端返回详细错误信息并在前端显示

### 主要改动
- `AnnotationFormRenderer.parseInputValue()`: 允许用户输入各种格式的值，不强制类型转换
- `AnnotationBuffer.validateField()`: 只检查必填项，移除复杂约束校验
- `AnnotationBuffer.handleSave()`: 处理后端返回的校验错误并显示给用户

### 使用说明
1. 用户可以在任何类型的字段中输入值
2. 前端会尝试进行基础的类型转换（如字符串转数字）
3. 如果转换失败，保持原始输入值
4. 点击保存时，后端会进行完整的数据校验
5. 如有错误，会在对应字段下方显示具体的错误信息

---

**重要**：请确保在执行任何Python命令前激活conda环境：`conda activate annotator`

## 数据验证策略

### 前端验证（轻量级）
- 只进行基本的必填字段检查
- 简单的类型转换和格式化
- 实时用户体验反馈

### 后端验证（严格校验）
- 基于 Pydantic 模型的完整数据验证
- 字段类型、约束条件、业务规则校验
- 自定义验证器和模型级验证
- 详细的错误信息返回

### 错误处理流程
1. 用户填写表单时，前端进行基础验证
2. 点击保存时，数据发送到后端
3. 后端使用 Pydantic 模板进行严格校验
4. 如果校验失败，返回详细错误信息
5. 前端接收错误信息并在对应字段显示
6. 用户修正错误后重新保存

## 技术栈

- **前端**: React 18 + TypeScript + Antd + Monaco Editor
- **后端**: FastAPI + Pydantic + Python 3.8+
- **数据存储**: 文件系统 (JSON)
- **权限管理**: JWT + 基于角色的访问控制

## 标注模板

系统支持基于 Pydantic 的动态标注模板：

```python
from pydantic import BaseModel, Field, field_validator
from typing import List

class CrimeAnalysis(BaseModel):
    """犯罪分析模型"""
    案件描述: str = Field("", description="案件描述")
    构成原因: str = Field("", description="构成犯罪的原因", 
                       json_schema_extra={"is_annotation": True})
    嫌疑人: str
    罪名: str
    基准刑_年: str = Field(description="基准刑期-年", 
                         json_schema_extra={"is_annotation": True})
    基准刑_月: str = Field(description="基准刑期-月", 
                         json_schema_extra={"is_annotation": True})
    
    @field_validator('基准刑_月')
    @classmethod
    def validate_months(cls, v: str) -> str:
        try:
            v_int = int(v)
        except ValueError:
            raise ValueError("必须是数字")
        if v_int >= 12:
            raise ValueError("月份应该小于12")
        return v
```

## 开发说明

### 添加新的验证规则
1. 在模板文件中添加 `@field_validator` 或 `@model_validator`
2. 重新上传模板到系统
3. 创建使用该模板的任务

### 调试验证功能
运行测试脚本验证 Pydantic 校验：
```bash
python test_validation.py
```

## 注意事项

1. 确保 conda 环境正确激活
2. 后端数据目录有适当的读写权限
3. 生产环境请修改默认密码和密钥
4. Monaco Editor 已优化错误处理，抑制 Worker 错误

## 贡献

欢迎提交 Issue 和 Pull Request。
