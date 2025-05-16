# 前端启动脚本

# 切换到前端目录
Set-Location "$PSScriptRoot\frontend"

# 设置环境变量，消除 CJS 警告
$env:NODE_OPTIONS="--no-warnings"

# 启动前端服务
Write-Host "正在启动前端服务..." -ForegroundColor Green
Write-Host "前端服务地址: http://localhost:3000" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Green

# 执行前端启动命令
npm run dev 