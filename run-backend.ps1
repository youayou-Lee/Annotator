# 后端启动脚本

# 激活 Conda 环境
Write-Host "正在激活 Conda 环境 (annotator)..." -ForegroundColor Yellow
conda activate annotator

# 检查 Conda 环境是否激活成功
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误：无法激活 Conda 环境，请确保已安装 Conda 并创建了 'annotator' 环境" -ForegroundColor Red
}

# 切换到后端目录
Set-Location "$PSScriptRoot\backend"

# 启动后端服务
Write-Host "正在启动后端服务..." -ForegroundColor Green
Write-Host "后端服务地址: http://localhost:8000" -ForegroundColor Cyan
Write-Host "按 Ctrl+C 可以停止服务" -ForegroundColor Yellow
Write-Host "=================================" -ForegroundColor Green

# 执行后端启动命令
uvicorn app.main:app --reload 