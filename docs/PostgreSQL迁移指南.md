# PostgreSQL数据库迁移指南

本文档描述了将文书标注系统从SQLite数据库迁移到PostgreSQL数据库的过程、步骤和注意事项。

## 简介

为了解决系统重启后数据丢失的问题，我们将数据库从SQLite迁移到PostgreSQL。PostgreSQL是一个功能强大的开源关系型数据库系统，提供了更好的数据持久化、并发处理和性能优化。

## 前提条件

- 已安装PostgreSQL数据库服务器（推荐版本：13.0或更高）
- 安装了psycopg2-binary库（用于Python连接PostgreSQL）
- 安装了SQLAlchemy和Alembic（用于数据库模型管理和迁移）

## 迁移步骤

### 1. 安装必要的依赖

```bash
# 激活项目的虚拟环境
conda activate annotator

# 安装PostgreSQL驱动和迁移工具
pip install psycopg2-binary alembic
```

### 2. 修改数据库配置

编辑 `backend/.env` 文件，修改数据库连接参数：

```
# 数据库配置
DATABASE_URL=postgresql://postgres:123456@localhost:5432/annotator
POSTGRES_USER=postgres
POSTGRES_PASSWORD=123456
POSTGRES_DB=annotator
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

### 3. 创建数据库和初始化表结构

我们提供了两个工具脚本来帮助创建和验证数据库：

#### 创建数据库和表结构

运行 `create_postgres_db.py` 脚本来创建数据库、初始化表结构并添加管理员用户：

```bash
cd backend
python create_postgres_db.py
```

该脚本会：
- 创建名为 `annotator` 的PostgreSQL数据库（如果不存在）
- 根据模型定义创建所有表
- 创建默认管理员用户（admin@example.com / admin）

#### 验证数据库连接

使用 `test_postgres_connection.py` 脚本测试数据库连接：

```bash
python test_postgres_connection.py
```

该脚本会：
- 测试到PostgreSQL数据库的连接
- 显示数据库版本信息
- 列出数据库中的表
- 显示用户表中的记录数量和用户列表

#### 检查表结构

使用 `test_postgres_schema.py` 脚本检查数据库表结构：

```bash
python test_postgres_schema.py
```

该脚本会：
- 列出所有表及其结构
- 显示每个表的列定义、主键、外键和索引
- 显示用户表中的记录

### 4. 运行系统

在完成数据库迁移后，可以正常启动系统：

```bash
cd ..
./run-backend.ps1
./run-frontend.ps1
```

## 数据结构

迁移后的主要数据库表包括：

- `users` - 用户信息
- `documents` - 文档信息
- `tasks` - 标注任务
- `annotations` - 标注结果
- `alembic_version` - 迁移版本控制

## 故障排除

### PostgreSQL服务未启动

如果连接测试失败，请检查PostgreSQL服务是否已启动：

1. 按 Win+R 打开运行对话框
2. 输入 `services.msc` 并按回车
3. 找到 "PostgreSQL" 服务并确保其状态为"正在运行"
4. 如果未运行，右键单击并选择"启动"

### 数据库连接参数错误

如果遇到连接问题，请验证 `.env` 文件中的连接参数是否正确：

- 用户名: postgres
- 密码: 123456
- 主机名: localhost
- 端口: 5432
- 数据库名称: annotator

### 手动创建数据库

如果自动创建失败，可以使用pgAdmin或命令行手动创建数据库：

```sql
CREATE DATABASE annotator;
```

## 维护建议

- 定期备份PostgreSQL数据库
- 监控数据库性能和空间使用情况
- 考虑设置数据库自动备份计划

## 恢复到SQLite（如有需要）

如果需要恢复到SQLite数据库，编辑 `.env` 文件：

```
DATABASE_URL=sqlite:///./annotator.db
```

然后运行：

```bash
python create_admin_simple.py 