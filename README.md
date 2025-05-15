# 文书标注系统

一个支持多用户协作的在线文书标注平台，用于处理和分析各类文书数据。

## 功能特点

- 文件上传与格式校验
- 多用户任务管理
- 动态表单标注
- 数据复审对比
- 自定义导出格式

## 技术栈

### 后端
- FastAPI 3.0+
- PostgreSQL 15+
- SQLAlchemy 2.0+
- Pydantic v2
- Redis
- Celery

### 前端
- React 18
- TypeScript 5
- Ant Design Pro
- Monaco Editor
- Zustand
- React Query

## 快速开始

### 环境要求
- Python 3.10+
- PostgreSQL 15+
- Redis 6+
- Node.js 18+

### 安装步骤

1. 克隆项目
```bash
git clone [项目地址]
cd annotator
```

2. 创建并激活虚拟环境
```bash
conda create -n annotator python=3.10
conda activate annotator
```

3. 安装依赖
```bash
# 安装后端依赖
pip install -r requirements.txt

# 安装前端依赖
cd frontend
npm install
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，配置必要的环境变量
```

5. 初始化数据库
```bash
# 创建数据库
createdb annotator

# 运行数据库迁移
alembic upgrade head
```

6. 启动服务
```bash
# 启动后端服务
uvicorn backend.main:app --reload

# 启动前端服务
cd frontend
npm run dev
```

## 项目结构

```
annotator/
├── backend/          # 后端代码
│   ├── app/         # 应用代码
│   ├── tests/       # 测试文件
│   └── main.py      # 入口文件
├── frontend/        # 前端代码
│   ├── src/        # 源代码
│   └── public/     # 静态资源
├── data/           # 文件存储
└── docs/           # 文档
```

## 开发指南

### 代码规范
- 使用 Black 进行代码格式化
- 使用 isort 进行导入排序
- 使用 flake8 进行代码检查
- 使用 mypy 进行类型检查

### 提交规范
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码格式调整
- refactor: 代码重构
- test: 测试相关
- chore: 构建过程或辅助工具的变动

## 测试

```bash
# 运行后端测试
pytest

# 运行前端测试
cd frontend
npm test
```

## 部署

### 开发环境
```bash
docker-compose up -d
```

### 生产环境
```bash
# 构建镜像
docker-compose -f docker-compose.prod.yml build

# 启动服务
docker-compose -f docker-compose.prod.yml up -d
```

## 文档

- [API文档](docs/API.md)
- [开发指南](docs/CONTRIBUTING.md)
- [变更日志](docs/CHANGELOG.md)

## 许可证

[MIT License](LICENSE)

## 贡献指南

请查看 [CONTRIBUTING.md](docs/CONTRIBUTING.md) 了解如何参与项目开发。 