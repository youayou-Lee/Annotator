@echo off
chcp 65001 >nul
echo 🚀 启动文书标注系统开发环境...

REM 检查conda是否安装
where conda >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到conda命令，请先安装Anaconda或Miniconda
    pause
    exit /b 1
)

REM 检查node是否安装
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到node命令，请先安装Node.js
    pause
    exit /b 1
)

REM 创建数据目录结构
echo 📁 创建数据目录...
if not exist "data\users" mkdir data\users
if not exist "data\public_files\documents" mkdir data\public_files\documents
if not exist "data\public_files\templates" mkdir data\public_files\templates
if not exist "data\public_files\exports" mkdir data\public_files\exports
if not exist "data\tasks" mkdir data\tasks
if not exist "data\uploads" mkdir data\uploads

REM 初始化数据文件
echo 📄 初始化数据文件...
if not exist "data\users\users.json" (
    echo {"users": []} > data\users\users.json
)

if not exist "data\tasks\tasks.json" (
    echo {"tasks": []} > data\tasks\tasks.json
)

REM 检查conda环境是否存在
conda env list | findstr "annotator" >nul
if %errorlevel% neq 0 (
    echo 🔧 创建conda环境 'annotator'...
    conda create -n annotator python=3.9 -y
)

REM 激活conda环境并安装后端依赖
echo 📦 安装后端依赖...
call conda activate annotator

if exist "requirements.txt" (
    pip install -r requirements.txt
)

REM 安装前端依赖
echo 📦 安装前端依赖...
if exist "package.json" (
    npm install
)

REM 启动后端服务
echo 🔧 启动后端服务...
start "Backend Server" cmd /k "conda activate annotator && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM 启动前端服务
echo 🔧 启动前端服务...
start "Frontend Server" cmd /k "npm run dev"

echo.
echo 🎉 开发环境启动完成！
echo.
echo 📍 访问地址:
echo    前端: http://localhost:3000
echo    后端API: http://localhost:8000
echo    API文档: http://localhost:8000/docs
echo.
echo ⚠️  注意: 请确保在conda环境 'annotator' 中运行Python命令

pause 