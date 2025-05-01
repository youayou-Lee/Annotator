# 文书标注系统

这是一个用于文书数据标注、处理和训练的系统。

## 功能特点

- 文书数据过滤和筛选
- 数据格式化存储
- 基础信息补全
- 任务管理
- 人工标注界面
- AI辅助审查
- OpenAI训练数据准备
- 模型训练和验证

## 项目结构

```
.
├── backend/                 # 后端代码
│   ├── app/                # 主应用代码
│   │   ├── api/           # API路由
│   │   ├── core/          # 核心配置
│   │   ├── models/        # 数据模型
│   │   ├── schemas/       # Pydantic模型
│   │   ├── services/      # 业务逻辑
│   │   └── utils/         # 工具函数
│   ├── tests/             # 测试代码
│   └── alembic/           # 数据库迁移
├── frontend/               # 前端代码
│   ├── src/               # 源代码
│   ├── public/            # 静态资源
│   └── package.json       # 依赖配置
└── docs/                  # 文档
```

## 安装和运行

### 后端

1. 创建虚拟环境：
```bash
conda create -n your_env_name python=3.9.5
conda activate your_env_name
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行服务器：
```bash
cd backend
uvicorn app.main:app --reload
```

### 前端

1. 安装依赖：
```bash
cd frontend
npm install
```

2. 运行开发服务器：
```bash
npm run dev
```

## 使用说明

1. 数据过滤：通过API上传基础文书数据，设置筛选条件
2. 格式化存储：将筛选后的数据按照指定格式存储
3. 基础补全：使用LLM进行基础信息补全
4. 任务管理：创建和管理标注任务
5. 人工标注：通过标注界面进行数据标注
6. AI审查：使用AI模型进行数据审查
7. 训练准备：将数据转换为OpenAI训练格式
8. 模型训练：上传数据并训练模型
9. 模型验证：使用验证集测试模型性能
