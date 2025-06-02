# API 文档获取脚本使用说明

## 📋 概述

我为你创建了两个脚本来从 SwaggerUI 获取 API 接口文档：

1. **`get_api_docs.py`** - 完整的 API 文档提取器
2. **`quick_api_list.py`** - 快速 API 列表查看器

## 🚀 快速开始

### 1. 确保环境准备

```bash
# 激活 conda 环境
conda activate annotator

# 确保后端服务正在运行
cd backend
python run.py
```

### 2. 使用快速列表查看器

```bash
# 快速查看 API 列表
python quick_api_list.py

# 指定不同的服务器地址
python quick_api_list.py --url http://localhost:8000

# 保存 API 列表到文件
python quick_api_list.py --save
```

**输出示例：**
```
🔍 正在获取 API 文档: http://localhost:8000/openapi.json

📋 API 名称: Document Annotation System
📋 版本: 1.0.0
📋 服务器: http://localhost:8000

📊 统计信息:
   总端点数: 25
   GET: 12
   POST: 8
   PUT: 3
   DELETE: 2

🔗 API 端点列表:
================================================================================

📁 Authentication
----------------------------------------
  🟡 POST   /api/auth/login              用户登录
  🟡 POST   /api/auth/register           用户注册
  🟢 GET    /api/auth/me                 获取当前用户信息
  🟡 POST   /api/auth/refresh            刷新访问令牌

📁 User Management
----------------------------------------
  🟢 GET    /api/users                   获取用户列表
  🟡 POST   /api/users                   创建用户
  🟢 GET    /api/users/{user_id}         获取用户详情
```

### 3. 使用完整文档提取器

```bash
# 生成所有格式的文档
python get_api_docs.py

# 只生成 Markdown 格式
python get_api_docs.py --format markdown

# 只生成 JSON 格式
python get_api_docs.py --format json

# 只获取原始 OpenAPI 规范
python get_api_docs.py --format openapi

# 指定不同的服务器地址
python get_api_docs.py --url http://localhost:8000
```

**生成的文件：**
- `api_documentation.md` - 详细的 Markdown 文档
- `api_documentation.json` - 简化的 JSON 格式文档
- `openapi_spec.json` - 原始 OpenAPI 规范
- `api_list.txt` - 简单的 API 列表（使用 --save 参数）

## 📖 详细功能说明

### get_api_docs.py 功能特点

1. **完整的 API 文档提取**
   - 从 OpenAPI JSON 端点获取完整规范
   - 解析所有端点的详细信息
   - 提取参数、请求体、响应等信息

2. **多种输出格式**
   - **Markdown**: 适合阅读和文档网站
   - **JSON**: 适合程序处理
   - **OpenAPI**: 原始规范，可导入其他工具

3. **详细的文档内容**
   - API 基本信息（标题、版本、描述）
   - 服务器信息
   - 按模块分组的端点
   - 每个端点的详细信息：
     - 请求方法和路径
     - 摘要和描述
     - 请求参数
     - 请求体格式
     - 响应格式和状态码

### quick_api_list.py 功能特点

1. **快速概览**
   - 快速显示所有 API 端点
   - 按模块分组显示
   - 彩色标识不同的 HTTP 方法

2. **统计信息**
   - 总端点数量
   - 各种 HTTP 方法的分布

3. **测试示例**
   - 自动生成常用端点的 curl 测试命令
   - 提供登录等常见操作的示例

## 🛠️ 高级用法

### 1. 批量处理多个环境

```bash
# 创建批处理脚本
cat > get_all_envs.sh << 'EOF'
#!/bin/bash
echo "获取开发环境 API 文档..."
python get_api_docs.py --url http://localhost:8000

echo "获取测试环境 API 文档..."
python get_api_docs.py --url http://test-server:8000

echo "获取生产环境 API 文档..."
python get_api_docs.py --url https://api.production.com
EOF

chmod +x get_all_envs.sh
./get_all_envs.sh
```

### 2. 定时更新文档

```bash
# 创建定时任务脚本
cat > update_docs.sh << 'EOF'
#!/bin/bash
cd /path/to/your/project
conda activate annotator
python get_api_docs.py
git add api_documentation.md
git commit -m "Update API documentation $(date)"
git push
EOF

# 添加到 crontab（每天更新一次）
# 0 2 * * * /path/to/update_docs.sh
```
