# 文书标注系统

这是一个用于法律文书数据处理、标注和训练的完整系统。系统支持从原始数据导入到模型训练的全流程处理。

## 系统架构

```
.
├── backend/                 # 后端服务
│   ├── app/                # 主应用
│   │   ├── api/           # API路由层
│   │   ├── core/          # 核心配置
│   │   ├── models/        # 数据模型
│   │   ├── schemas/       # 数据验证模式
│   │   └── services/      # 业务逻辑层
├── frontend/               # 前端应用
│   ├── src/               # 源代码
│   │   ├── components/    # 通用组件
│   │   ├── views/         # 页面组件
│   │   └── router/        # 路由配置
└── data/                  # 数据存储
    ├── raw/               # 原始数据
    ├── formatted/         # 格式化数据
    ├── annotations/       # 标注结果
    ├── task_templates/    # 任务模板
    └── merged_data/       # 合并后的数据

```

## 功能模块

### 1. 数据处理流程 (backend/app/services/file_service.py)
- 文件上传：支持大规模JSON/JSONL格式的文书数据上传
- 数据验证：确保上传数据的完整性和格式正确性
- 文件管理：统一管理上传的文件，支持查询和检索

### 2. 数据过滤 (backend/app/services/filter_service.py)
- 条件筛选：支持多维度的数据筛选（法院、案件类型等）
- 内容过滤：支持基于文本内容的精确匹配
- 批量处理：支持对大规模数据进行高效过滤

### 3. 格式化处理 (backend/app/services/format_service.py)
- 模板管理：支持自定义数据格式化模板
- 批量转换：将原始数据转换为标准格式
- 数据验证：确保转换后的数据符合预期格式

### 4. 任务管理 (backend/app/services/task_service.py)
- 任务创建：支持创建不同类型的标注任务
- 任务分配：管理任务分配和进度跟踪
- 状态管理：实时监控任务完成情况
- 模板配置：支持自定义任务模板

### 5. 人工标注 (backend/app/services/annotator_service.py)
- 标注界面：直观的Web标注界面
- 实时保存：自动保存标注进度
- 批注验证：确保标注数据的质量
- 进度追踪：实时显示标注进度

### 6. AI辅助审查 (backend/app/services/ai_review_service.py)
- AI审查：使用GPT模型辅助审查标注结果
- 对比分析：比较AI审查和人工标注的差异
- 质量控制：提供标注质量的客观评估

### 7. 训练数据准备 (backend/app/services/training_service.py)
- 数据转换：将标注数据转换为训练格式
- 数据集划分：自动划分训练集和验证集
- 格式验证：确保数据符合训练要求

### 8. 模型训练和验证
- OpenAI接入：支持直接提交到OpenAI进行训练
- 训练监控：实时监控训练进度
- 模型验证：使用验证集评估模型性能

## 快速开始

### 后端服务

1. 创建Python虚拟环境：
```bash
conda create -n annotator python=3.9.5
conda activate annotator
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 启动服务：
```bash
cd backend
uvicorn app.main:app --reload
```

### 前端应用

1. 安装依赖：
```bash
cd frontend
npm install
```

2. 启动开发服务器：
```bash
npm run dev
```

## 使用流程

1. 数据导入
   - 通过Web界面上传原始文书数据
   - 系统自动验证数据格式

2. 数据过滤
   - 设置过滤条件（法院、案件类型等）
   - 执行过滤，获取目标数据集

3. 格式化处理
   - 选择或创建格式化模板
   - 执行格式化转换

4. 任务创建
   - 创建标注任务
   - 配置任务参数和标注要求

5. 人工标注
   - 分配标注任务
   - 进行标注工作
   - 保存标注结果

6. AI审查
   - 配置审查模板
   - 执行AI辅助审查
   - 分析审查结果

7. 训练准备
   - 合并标注结果
   - 转换为训练格式
   - 划分数据集

8. 模型训练
   - 提交训练任务
   - 监控训练进度
   - 验证模型效果
