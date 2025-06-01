#!/bin/bash

# 文书标注系统开发环境启动脚本

echo "🚀 启动文书标注系统开发环境..."

# 检查conda是否安装
if ! command -v conda &> /dev/null; then
    echo "❌ 错误: 未找到conda命令，请先安装Anaconda或Miniconda"
    exit 1
fi

# 检查node是否安装
if ! command -v node &> /dev/null; then
    echo "❌ 错误: 未找到node命令，请先安装Node.js"
    exit 1
fi

# 创建数据目录结构
echo "📁 创建数据目录..."
mkdir -p data/{users,public_files/{documents,templates,exports},tasks,uploads}

# 初始化数据文件
echo "📄 初始化数据文件..."
if [ ! -f "data/users/users.json" ]; then
    echo '{"users": []}' > data/users/users.json
fi

if [ ! -f "data/tasks/tasks.json" ]; then
    echo '{"tasks": []}' > data/tasks/tasks.json
fi

# 检查conda环境是否存在
if ! conda env list | grep -q "annotator"; then
    echo "🔧 创建conda环境 'annotator'..."
    conda create -n annotator python=3.9 -y
fi

# 激活conda环境并安装后端依赖
echo "📦 安装后端依赖..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate annotator

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

# 安装前端依赖
echo "📦 安装前端依赖..."
if [ -f "package.json" ]; then
    npm install
fi

# 启动后端服务（后台运行）
echo "🔧 启动后端服务..."
conda activate annotator
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &

# 启动前端服务
echo "🔧 启动前端服务..."
npm run dev &

echo ""
echo "🎉 开发环境启动完成！"
echo ""
echo "📍 访问地址:"
echo "   前端: http://localhost:3000"
echo "   后端API: http://localhost:8000"
echo "   API文档: http://localhost:8000/docs"
echo ""
echo "⚠️  注意: 请确保在conda环境 'annotator' 中运行Python命令" 