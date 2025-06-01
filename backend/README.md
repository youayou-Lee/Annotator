# 文书标注系统 - 后端

基于 FastAPI 的文书标注系统后端服务。

## 功能特性

- 🔐 JWT 认证系统
- 👥 用户管理（超级管理员、管理员、标注员）
- 📁 文件管理（上传、下载、预览）
- 📋 任务管理（创建、分配、跟踪）
- ✏️ 标注功能（标注、提交、复审）
- 📊 权限控制
- 💾 文件系统存储

## 技术栈

- **框架**: FastAPI 0.104.1
- **认证**: JWT (python-jose)
- **密码加密**: bcrypt (passlib)
- **数据验证**: Pydantic 2.6.1
- **文件处理**: aiofiles, python-multipart
- **服务器**: Uvicorn

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # 应用入口
│   ├── config.py            # 配置管理
│   ├── models/              # 数据模型
│   │   ├── __init__.py
│   │   ├── user.py          # 用户模型
│   │   ├── task.py          # 任务模型
│   │   ├── annotation.py    # 标注模型
│   │   ├── file.py          # 文件模型
│   │   └── auth.py          # 认证模型
│   ├── core/                # 核心功能
│   │   ├── __init__.py
│   │   ├── security.py      # 安全认证
│   │   └── storage.py       # 存储管理
│   └── api/                 # API路由
│       ├── __init__.py
│       ├── auth.py          # 认证接口
│       ├── users.py         # 用户管理
│       ├── files.py         # 文件管理
│       ├── tasks.py         # 任务管理
│       └── annotations.py   # 标注功能
├── data/                    # 数据目录（自动创建）
├── .env.example             # 环境配置示例
├── run.py                   # 启动脚本
└── README.md
```

## 快速开始

### 1. 环境准备

确保已激活 conda 环境：
```bash
conda activate annotator
```

### 2. 安装依赖

```bash
pip install -r ../requirements.txt
```

### 3. 配置环境

复制环境配置文件：
```bash
cp .env.example .env
```

编辑 `.env` 文件，修改必要的配置项（特别是 SECRET_KEY）。

### 4. 启动服务

```bash
python run.py
```

或者使用 uvicorn 直接启动：
```bash
uvicorn app.main:app --reload --port 8000
```

### 5. 访问服务

- 服务地址: http://localhost:8000
- API 文档: http://localhost:8000/docs
- ReDoc 文档: http://localhost:8000/redoc

## API 接口

### 认证接口
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/register` - 用户注册
- `GET /api/auth/me` - 获取当前用户信息

### 用户管理
- `GET /api/users` - 获取用户列表
- `GET /api/users/{user_id}` - 获取用户详情
- `PUT /api/users/{user_id}` - 更新用户信息

### 文件管理
- `GET /api/files` - 获取文件列表
- `POST /api/files/upload` - 上传文件
- `DELETE /api/files/{file_id}` - 删除文件
- `GET /api/files/{file_id}/download` - 下载文件
- `GET /api/files/{file_id}/preview` - 预览文件

### 任务管理
- `GET /api/tasks` - 获取任务列表
- `POST /api/tasks` - 创建任务
- `GET /api/tasks/{task_id}` - 获取任务详情
- `PUT /api/tasks/{task_id}` - 更新任务
- `DELETE /api/tasks/{task_id}` - 删除任务
- `POST /api/tasks/{task_id}/export` - 导出任务数据

### 标注功能
- `GET /api/tasks/{task_id}/documents/{document_id}/annotation` - 获取标注数据
- `POST /api/tasks/{task_id}/documents/{document_id}/annotation` - 保存标注数据
- `POST /api/tasks/{task_id}/documents/{document_id}/submit` - 提交标注
- `GET /api/tasks/{task_id}/documents/{document_id}/review` - 获取复审数据
- `POST /api/tasks/{task_id}/documents/{document_id}/review` - 提交复审

## 数据存储

系统使用文件系统存储，数据目录结构：

```
data/
├── users/
│   └── users.json              # 用户信息
├── public_files/               # 公共文件库
│   ├── documents/              # 文档文件
│   ├── templates/              # 模板文件
│   └── exports/                # 导出文件
├── tasks/
│   ├── tasks.json              # 任务列表
│   └── {task_id}/
│       └── annotations/        # 标注数据
└── uploads/                    # 临时上传文件
```

## 权限控制

| 功能 | super_admin | admin | annotator |
|------|-------------|-------|-----------|
| 用户管理 | ✅ | ✅ | ❌ |
| 文件上传 | ✅ | ✅ | ✅ |
| 文件删除 | ✅ | ✅ | 仅自己上传 |
| 任务创建 | ✅ | ✅ | 仅分配给自己 |
| 任务分配 | ✅ | ✅ | ❌ |
| 标注工作 | ✅ | ✅ | ✅ |
| 复审功能 | ✅ | ✅ | ❌ |

## 开发说明

### 添加新的API接口

1. 在 `app/models/` 中定义数据模型
2. 在 `app/api/` 中创建路由文件
3. 在 `app/api/__init__.py` 中注册路由
4. 在 `app/core/storage.py` 中添加存储逻辑（如需要）

### 扩展存储功能

当前使用文件系统存储，如需扩展为数据库存储：

1. 修改 `app/core/storage.py`
2. 添加数据库连接配置
3. 实现对应的 CRUD 操作

## 注意事项

1. 生产环境请修改 `SECRET_KEY`
2. 确保 `data` 目录有适当的读写权限
3. 定期备份 `data` 目录中的重要数据
4. 监控磁盘空间使用情况 