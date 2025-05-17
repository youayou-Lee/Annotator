# 后台启动服务脚本-此脚本适用于AI调用。
# GBK2312

Write-Host "正在准备启动服务..." -ForegroundColor Cyan

# 清理现有作业
Write-Host "清理现有作业..." -ForegroundColor Yellow
Get-Job | Where-Object { $_.State -eq "Running" } | Stop-Job
Get-Job | Remove-Job

# 创建日志目录
$logDir = ".\logs"
if (-not (Test-Path $logDir)) {
    New-Item -Path $logDir -ItemType Directory -Force | Out-Null
    Write-Host "已创建日志目录: $logDir" -ForegroundColor Green
}

# 启动后端服务
Write-Host "启动后端服务..." -ForegroundColor Green
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    .\run-backend.ps1
} -Name "BackendService"

# 启动前端服务
Write-Host "启动前端服务..." -ForegroundColor Green
$frontendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    .\run-frontend.ps1
} -Name "FrontendService"

# 显示作业信息
Write-Host "服务已在后台启动:" -ForegroundColor Cyan
Write-Host "- 后端服务: 作业ID $($backendJob.Id)" -ForegroundColor Green
Write-Host "- 前端服务: 作业ID $($frontendJob.Id)" -ForegroundColor Green

# 显示作业状态
Get-Job | Format-Table -Property Id, Name, State

# 提供帮助信息
Write-Host "`n使用以下命令查看日志:" -ForegroundColor Magenta
Write-Host "Receive-Job -Id $($backendJob.Id) -Keep" -ForegroundColor White
Write-Host "Receive-Job -Id $($frontendJob.Id) -Keep" -ForegroundColor White

Write-Host "`n使用以下命令停止服务:" -ForegroundColor Magenta
Write-Host "Stop-Job -Id $($backendJob.Id); Stop-Job -Id $($frontendJob.Id)" -ForegroundColor White