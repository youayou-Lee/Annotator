#!/bin/bash

# 文书标注系统开发环境停止脚本

echo "🛑 停止文书标注系统开发环境..."

# 停止uvicorn进程
echo "🔧 停止后端服务..."
pkill -f "uvicorn.*app.main:app"

# 停止npm/node进程
echo "🔧 停止前端服务..."
pkill -f "npm.*run.*dev"
pkill -f "node.*vite"

echo ""
echo "🎉 开发环境已停止！" 