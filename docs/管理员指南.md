# 文书标注系统管理员指南

## 目录

1. [系统概述](#系统概述)
2. [环境要求](#环境要求)
3. [系统安装](#系统安装)
4. [初始配置](#初始配置)
5. [用户管理](#用户管理)
6. [数据管理](#数据管理)
7. [系统维护](#系统维护)
8. [常见问题排除](#常见问题排除)
9. [附录](#附录)

## 系统概述

文书标注系统是一个专为法律文书标注设计的平台，支持文书上传、格式校验、标注任务分配和管理、数据导出等功能。系统采用前后端分离架构，前端使用React开发，后端使用FastAPI框架，数据存储采用PostgreSQL数据库。

### 系统架构

- **前端**：React + TypeScript + Ant Design
- **后端**：Python FastAPI
- **数据库**：PostgreSQL
- **部署**：Docker容器化部署（可选）

## 环境要求

### 硬件要求

- CPU: 双核处理器或更高
- 内存: 至少4GB RAM，建议8GB+
- 存储空间: 至少20GB可用空间

### 软件要求

- 操作系统: Windows 10/11, Linux (Ubuntu 20.04+), macOS
- Node.js: v16.0+
- Python: 3.9+
- PostgreSQL: 13.0+
- Conda环境管理器
- Git版本控制

## 系统安装

### 获取源代码

```bash
git clone https://github.com/your-organization/annotator.git
cd annotator
```

### 后端安装

1. 使用Conda创建并激活虚拟环境

```bash
conda create -n annotator python=3.9
conda activate annotator
```

2. 安装后端依赖包

```bash
pip install -r requirements.txt
```

3. 配置数据库

```bash
# 使用alembic创建数据库表
cd backend
alembic upgrade head
```

4. 初始化基础数据

```bash
python -m app.initial_data
```

### 前端安装

1. 安装前端依赖

```bash
cd frontend
npm install
```

2. 编译前端代码（生产环境）

```bash
npm run build
```

## 初始配置

### 配置文件说明

系统配置主要集中在以下文件中：

- `backend/.env`: 后端环境变量配置
- `backend/app/core/config.py`: 核心配置参数
- `frontend/.env`: 前端环境变量配置

### 基础配置项

#### 后端配置 (.env文件)

```
# 数据库连接
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=yourpassword
POSTGRES_DB=annotator

# 安全设置
SECRET_KEY=yoursecretkey
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24小时

# 文件存储
UPLOAD_FOLDER=./uploads
MAX_CONTENT_LENGTH=10485760  # 10MB
```

#### 前端配置 (.env文件)

```
VITE_API_URL=http://localhost:8000/api/v1
VITE_APP_NAME=文书标注系统
VITE_DEFAULT_TIMEOUT=10000  # 10秒
```

### 启动系统

系统提供了一键启动脚本`start-annotator.ps1`（Windows）或`start-annotator.sh`（Linux/macOS），执行该脚本将同时启动前端和后端服务。

```
# Windows
.\start-annotator.ps1

# Linux/macOS
./start-annotator.sh
```

启动后，前端服务运行在http://localhost:3000，后端服务运行在http://localhost:8000。

## 用户管理

### 默认账户

系统初始安装后，自动创建以下默认账户：

| 角色 | 用户名 | 密码 | 说明 |
|------|--------|------|------|
| 超级管理员 | admin | admin123 | 拥有所有权限，包括创建其他管理员 |
| 示例标注员 | annotator | anno123 | 用于测试的标注人员账户 |

**重要**: 首次登录后请立即修改默认密码！

### 用户角色与权限

系统定义了以下角色：

1. **超级管理员**：
   - 拥有所有系统权限
   - 可管理其他管理员账户
   - 可修改系统配置

2. **管理员**：
   - 管理标注人员账户
   - 管理文书和任务
   - 查看统计报告
   - 导出标注数据

3. **标注人员**：
   - 执行分配的标注任务
   - 查看自己的历史任务
   - 更新个人资料

### 用户管理操作

#### 创建新用户

1. 登录管理员账户
2. 进入"用户管理"页面
3. 点击"添加用户"按钮
4. 填写以下信息：
   - 用户名（必填）：用于登录，不可重复
   - 密码（必填）：至少8个字符
   - 角色（必选）：管理员或标注人员
   - 电子邮件（选填）：用于通知和密码重置
   - 姓名（选填）：用户真实姓名
5. 点击"确认"完成创建

#### 编辑用户信息

1. 在用户列表中找到目标用户
2. 点击"编辑"按钮
3. 修改用户信息
4. 点击"保存"确认修改

#### 禁用/启用用户

1. 在用户列表中找到目标用户
2. 切换"状态"开关
3. 确认操作

被禁用的用户无法登录系统，但其账户信息和历史数据保留。

#### 删除用户

1. 在用户列表中找到目标用户
2. 点击"删除"按钮
3. 在确认对话框中点击"确认"

**注意**：删除用户将同时删除其所有任务记录和标注数据，且无法恢复。建议使用禁用功能替代删除。

## 数据管理

### 文件存储

系统中的文件存储在以下目录：

- 上传文件：`backend/uploads/`
- 标注结果：`backend/data/annotations/`
- 导出文件：`backend/data/exports/`

这些目录可在配置文件中修改。

### 数据备份

#### 数据库备份

建议定期备份PostgreSQL数据库：

```bash
# 备份数据库
pg_dump -h localhost -U postgres -F c -b -v -f annotator_backup.dump annotator

# 恢复数据库
pg_restore -h localhost -U postgres -d annotator annotator_backup.dump
```

#### 文件备份

定期备份上传和标注文件：

```bash
# 备份文件
tar -czf annotator_files_backup.tar.gz backend/uploads backend/data
```

### 数据清理

系统提供了数据清理工具，可通过管理界面的"系统设置">"数据管理"访问：

- **临时文件清理**：删除已处理但未关联任务的上传文件
- **导出文件清理**：删除超过30天的导出文件
- **日志清理**：删除超过90天的系统日志

## 系统维护

### 日志管理

系统日志存储在以下位置：

- 后端日志：`backend/logs/`
- 前端日志：浏览器控制台和本地存储

通过管理界面的"系统设置">"日志设置"可调整日志级别：

- **ERROR**：只记录错误信息
- **WARNING**：记录警告和错误
- **INFO**：记录一般信息（默认）
- **DEBUG**：记录详细调试信息

### 性能监控

系统提供了基本的性能监控功能，可通过管理界面的"系统状态"页面查看：

- CPU和内存使用率
- 数据库连接状态
- API响应时间
- 活跃用户会话

### 系统更新

更新系统到新版本：

1. 备份数据库和文件
2. 拉取最新代码：
   ```bash
   git pull origin main
   ```
3. 更新依赖：
   ```bash
   # 后端
   conda activate annotator
   pip install -r requirements.txt
   
   # 前端
   cd frontend
   npm install
   ```
4. 应用数据库迁移：
   ```bash
   cd backend
   alembic upgrade head
   ```
5. 重新编译前端（如需要）：
   ```bash
   cd frontend
   npm run build
   ```
6. 重启服务

## 常见问题排除

### 登录问题

**问题**：管理员无法登录系统

**解决方案**：
1. 检查数据库连接是否正常
2. 尝试重置管理员密码：
   ```bash
   cd backend
   python -m app.reset_admin_password
   ```

### 数据库连接问题

**问题**：系统报告无法连接数据库

**解决方案**：
1. 确认PostgreSQL服务是否运行
2. 检查`.env`文件中的数据库连接参数
3. 确认数据库用户具有足够权限

### 文件上传问题

**问题**：文件上传失败或长时间无响应

**解决方案**：
1. 检查`backend/app/core/config.py`中的文件大小限制
2. 确认上传目录权限正确
3. 检查磁盘空间是否充足

### API响应缓慢

**问题**：系统操作响应缓慢

**解决方案**：
1. 检查数据库查询性能，可能需要添加索引
2. 确认服务器资源是否足够
3. 考虑增加数据库连接池大小（在`config.py`中设置）

## 附录

### 命令行工具

系统提供以下命令行工具：

- **创建管理员**：
  ```bash
  python -m app.create_admin --username admin2 --password secure123
  ```

- **重置数据库**：
  ```bash
  python -m app.reset_db
  ```

- **导入示例数据**：
  ```bash
  python -m app.import_sample_data
  ```

### 环境变量参考

完整的环境变量列表可在`backend/app/core/config.py`文件中查看。

### API文档

API文档可通过访问以下地址获取：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 技术支持

如有任何技术问题，请联系系统开发团队：

- 电子邮件：support@example.com
- 问题跟踪：https://github.com/your-organization/annotator/issues 