# 后台服务启动脚本 GBK2312
Write-Host "正在准备启动服务..." -ForegroundColor Cyan

# 清理已有作业 - 改进版
Write-Host "清理现有作业..." -ForegroundColor Yellow
$runningJobs = Get-Job | Where-Object { $_.State -eq "Running" }
foreach ($job in $runningJobs) {
    Write-Host "正在停止作业ID: $($job.Id), 名称: $($job.Name)" -ForegroundColor Yellow
    try {
        # 使用10秒超时停止作业
        $job | Stop-Job -Timeout 10 -ErrorAction SilentlyContinue
        
        # 如果作业仍在运行，尝试强制停止
        if ((Get-Job -Id $job.Id).State -eq "Running") {
            Write-Host "作业 $($job.Id) 未能正常停止，尝试强制停止..." -ForegroundColor Red
            $job | Stop-Job -PassThru -ErrorAction SilentlyContinue | Remove-Job -Force -ErrorAction SilentlyContinue
        }
    }
    catch {
        Write-Host "停止作业 $($job.Id) 时出错: $_" -ForegroundColor Red
    }
}

# 清理所有作业
Get-Job | Remove-Job -Force -ErrorAction SilentlyContinue

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
Write-Host "服务已在后台运行:" -ForegroundColor Cyan
Write-Host "- 后端服务: 作业ID $($backendJob.Id)" -ForegroundColor Green
Write-Host "- 前端服务: 作业ID $($frontendJob.Id)" -ForegroundColor Green

# 显示作业状态
Get-Job | Format-Table -Property Id, Name, State

# 提供帮助信息
Write-Host "`n使用以下命令查看日志:" -ForegroundColor Magenta
Write-Host "Receive-Job -Id $($backendJob.Id) -Keep" -ForegroundColor White
Write-Host "Receive-Job -Id $($frontendJob.Id) -Keep" -ForegroundColor White

Write-Host "`n使用以下命令停止服务:" -ForegroundColor Magenta
Write-Host "Stop-Job -Id $($backendJob.Id) -Timeout 10; Stop-Job -Id $($frontendJob.Id) -Timeout 10" -ForegroundColor White

# 创建一个专用的停止服务函数
Write-Host "`n或使用以下函数停止所有服务:" -ForegroundColor Magenta
Write-Host 'function Stop-AllServices { 
  param([int]$Timeout = 10)
  $jobs = Get-Job
  Write-Host "正在停止 $($jobs.Count) 个服务..." -ForegroundColor Yellow
  foreach ($job in $jobs) {
    Write-Host "停止作业: $($job.Id) - $($job.Name)" -ForegroundColor Cyan
    try {
      Stop-Job -Id $job.Id -Timeout $Timeout -ErrorAction SilentlyContinue
      if ((Get-Job -Id $job.Id -ErrorAction SilentlyContinue).State -eq "Running") {
        Write-Host "强制停止作业: $($job.Id)" -ForegroundColor Red
        Remove-Job -Id $job.Id -Force -ErrorAction SilentlyContinue
      }
    } catch {
      Write-Host "错误: $_" -ForegroundColor Red
    }
  }
  Write-Host "所有服务已停止" -ForegroundColor Green
}
Stop-AllServices' -ForegroundColor White