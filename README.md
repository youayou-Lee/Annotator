# 文书标注系统

一个支持多用户协作的在线文书标注平台，采用前后端分离架构，数据存储在文件系统中。

## 🚀 功能特性

- **文件管理**：支持文档、模板和导出文件的管理
- **任务管理**：创建、分配和跟踪标注任务
- **智能标注**：基于模板的动态表单生成
- **复审功能**：对比和审核标注结果
- **权限控制**：支持管理员、超级管理员和标注人员三种角色

## 📋 环境要求

- Python 3.9+ (需要conda环境)
- Node.js 16+

## 🛠️ 快速开始

### 1. 安装依赖

```bash
# 创建conda环境
conda create -n annotator python=3.9
conda activate annotator

# 安装后端依赖
pip install -r requirements.txt

# 安装前端依赖
npm install
```

### 2. 初始化数据

```bash
# 创建数据目录
mkdir -p data/{users,public_files/{documents,templates,exports},tasks,uploads}

# 初始化数据文件
echo '{"users": []}' > data/users/users.json
echo '{"tasks": []}' > data/tasks/tasks.json
```

### 3. 启动服务

```bash
# 启动后端 (确保在conda环境中)
conda activate annotator
uvicorn app.main:app --reload --port 8000

# 启动前端
npm run dev
```

### 4. 访问系统

- 前端：http://localhost:3000
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

## 📁 项目结构

```
├── data/                  # 数据存储目录
├── requirements.txt       # Python依赖
├── package.json          # 前端依赖
├── docker-compose.yml    # Docker配置
├── start-dev.bat         # Windows启动脚本
├── start-dev.sh          # Linux/Mac启动脚本
└── docs/                 # 文档
    ├── 系统设计文档.md
    ├── 文档验证模板指南.md
    └── 产品需求.md
```

## 🔐 权限说明

| 功能 | 超级管理员 | 管理员 | 标注人员 |
|------|-----------|--------|----------|
| 用户管理 | ✅ | ✅ | ❌ |
| 文件管理 | ✅ | ✅ | 部分 |
| 任务管理 | ✅ | ✅ | 部分 |
| 标注工作 | ✅ | ✅ | ✅ |
| 复审功能 | ✅ | ✅ | ❌ |

## 📝 模板开发

标注模板是Python文件，定义标注字段：

```python
TEMPLATE_INFO = {
    "name": "标注模板",
    "version": "1.0.0",
    "description": "模板描述"
}

ANNOTATION_FIELDS = [
    {
        "name": "title",
        "type": "string",
        "required": True,
        "description": "标题"
    }
]
```

详细说明请参考 [文档验证模板指南](docs/文档验证模板指南.md)

## 🚀 部署

### 开发环境
使用提供的启动脚本：
- Windows: `start-dev.bat`
- Linux/Mac: `start-dev.sh`

### 生产环境
```bash
docker-compose up -d
```

## ⚠️ 注意事项

- 必须在conda环境 `annotator` 中运行Python命令
- 确保数据目录有正确的读写权限
- 首次运行需要创建管理员账户

---

**重要**：请确保在执行任何Python命令前激活conda环境：`conda activate annotator`
