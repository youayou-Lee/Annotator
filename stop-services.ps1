# 停止服务快捷脚本
Write-Host "正在准备停止服务..." -ForegroundColor Cyan

function Stop-AllServices { 
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
      } else {
        Write-Host "作业 $($job.Id) 已成功停止" -ForegroundColor Green
      }
    } catch {
      Write-Host "错误: $_" -ForegroundColor Red
    }
  }
  
  # 清理所有作业
  $remainingJobs = Get-Job
  if ($remainingJobs.Count -gt 0) {
    Write-Host "清理残余作业..." -ForegroundColor Yellow
    Get-Job | Remove-Job -Force -ErrorAction SilentlyContinue
  }
  
  Write-Host "所有服务已停止" -ForegroundColor Green
}

# 执行停止
Stop-AllServices

# 显示当前作业状态
Write-Host "`n当前作业状态:" -ForegroundColor Magenta
Get-Job | Format-Table -Property Id, Name, State 