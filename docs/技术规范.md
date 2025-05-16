# 文书标注系统技术规范文档

## 1. 技术栈

### 1.1 后端技术栈
- 框架：FastAPI 3.0+
- 数据库：PostgreSQL 15+
- ORM：SQLAlchemy 2.0+
- 数据验证：Pydantic v2
- 缓存：Redis
- 异步任务：Celery
- 认证：JWT
- 文件存储：本地文件系统

### 1.2 前端技术栈
- 框架：React 18
- 语言：TypeScript 5
- UI库：Ant Design Pro
- 编辑器：Monaco Editor
- 状态管理：Zustand
- 数据请求：React Query
- 构建工具：Vite

## 2. 项目结构

```
annotator/
├── backend/
│   ├── app/
│   │   ├── api/          # API路由
│   │   ├── core/         # 核心配置
│   │   ├── db/           # 数据库配置
│   │   ├── models/       # 数据模型
│   │   ├── schemas/      # Pydantic模型
│   │   └── services/     # 业务逻辑
│   ├── tests/            # 测试文件
│   └── main.py           # 入口文件
├── frontend/
│   ├── src/
│   │   ├── components/   # 组件
│   │   ├── pages/        # 页面
│   │   ├── services/     # API服务
│   │   └── utils/        # 工具函数
│   └── package.json
├── data/                 # 文件存储
└── docs/                 # 文档
```

## 3. 数据库设计

### 3.1 核心表结构
```sql
-- 用户表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 任务表
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    creator_id INTEGER REFERENCES users(id),
    assignee_id INTEGER REFERENCES users(id),
    status VARCHAR(20) NOT NULL,
    original_file_path VARCHAR(255),
    annotated_file_path VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 标注规则表
CREATE TABLE annotation_rules (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks(id),
    field_name VARCHAR(100) NOT NULL,
    field_type VARCHAR(50) NOT NULL,
    validation_rules JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## 4. API规范

### 4.1 基础URL
```
/api/v1
```

### 4.2 认证方式
- Bearer Token认证
- Token过期时间：30分钟
- 刷新Token机制

### 4.3 响应格式
```json
{
    "code": 200,
    "message": "success",
    "data": {}
}
```

### 4.4 错误码
- 200: 成功
- 400: 请求参数错误
- 401: 未认证
- 403: 无权限
- 404: 资源不存在
- 500: 服务器错误

## 5. 开发规范

### 5.1 代码风格
- Python: Black + isort
- TypeScript: ESLint + Prettier
- 提交信息: Conventional Commits

### 5.2 测试要求
- 单元测试覆盖率 > 80%
- 集成测试覆盖主要功能
- E2E测试覆盖关键流程

### 5.3 文档要求
- API文档（OpenAPI）
- 代码注释
- 部署文档
- 用户手册

## 6. 部署方案

### 6.1 开发环境
- Docker Compose
- 本地开发服务器
- 热重载支持

### 6.2 生产环境
- Docker容器化
- Nginx反向代理
- PostgreSQL主从复制
- Redis集群
- 文件备份策略

## 7. 安全措施

### 7.1 应用安全
- 输入验证
- SQL注入防护
- XSS防护
- CSRF防护
- 文件上传安全

### 7.2 数据安全
- 数据加密
- 访问控制
- 操作日志
- 数据备份

## 8. 性能优化

### 8.1 后端优化
- 数据库索引
- 查询优化
- 缓存策略
- 异步处理

### 8.2 前端优化
- 代码分割
- 懒加载
- 缓存策略
- 性能监控 