# ��̨���������ű� GBK2312
Write-Host "����׼����������..." -ForegroundColor Cyan

# ����������ҵ - �Ľ���
Write-Host "����������ҵ..." -ForegroundColor Yellow
$runningJobs = Get-Job | Where-Object { $_.State -eq "Running" }
foreach ($job in $runningJobs) {
    Write-Host "����ֹͣ��ҵID: $($job.Id), ����: $($job.Name)" -ForegroundColor Yellow
    try {
        # ʹ��10�볬ʱֹͣ��ҵ
        $job | Stop-Job -Timeout 10 -ErrorAction SilentlyContinue
        
        # �����ҵ�������У�����ǿ��ֹͣ
        if ((Get-Job -Id $job.Id).State -eq "Running") {
            Write-Host "��ҵ $($job.Id) δ������ֹͣ������ǿ��ֹͣ..." -ForegroundColor Red
            $job | Stop-Job -PassThru -ErrorAction SilentlyContinue | Remove-Job -Force -ErrorAction SilentlyContinue
        }
    }
    catch {
        Write-Host "ֹͣ��ҵ $($job.Id) ʱ����: $_" -ForegroundColor Red
    }
}

# ����������ҵ
Get-Job | Remove-Job -Force -ErrorAction SilentlyContinue

# ������־Ŀ¼
$logDir = ".\logs"
if (-not (Test-Path $logDir)) {
    New-Item -Path $logDir -ItemType Directory -Force | Out-Null
    Write-Host "�Ѵ�����־Ŀ¼: $logDir" -ForegroundColor Green
}

# ������˷���
Write-Host "������˷���..." -ForegroundColor Green
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    .\run-backend.ps1
} -Name "BackendService"

# ����ǰ�˷���
Write-Host "����ǰ�˷���..." -ForegroundColor Green
$frontendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    .\run-frontend.ps1
} -Name "FrontendService"

# ��ʾ��ҵ��Ϣ
Write-Host "�������ں�̨����:" -ForegroundColor Cyan
Write-Host "- ��˷���: ��ҵID $($backendJob.Id)" -ForegroundColor Green
Write-Host "- ǰ�˷���: ��ҵID $($frontendJob.Id)" -ForegroundColor Green

# ��ʾ��ҵ״̬
Get-Job | Format-Table -Property Id, Name, State

# �ṩ������Ϣ
Write-Host "`nʹ����������鿴��־:" -ForegroundColor Magenta
Write-Host "Receive-Job -Id $($backendJob.Id) -Keep" -ForegroundColor White
Write-Host "Receive-Job -Id $($frontendJob.Id) -Keep" -ForegroundColor White

Write-Host "`nʹ����������ֹͣ����:" -ForegroundColor Magenta
Write-Host "Stop-Job -Id $($backendJob.Id) -Timeout 10; Stop-Job -Id $($frontendJob.Id) -Timeout 10" -ForegroundColor White

# ����һ��ר�õ�ֹͣ������
Write-Host "`n��ʹ�����º���ֹͣ���з���:" -ForegroundColor Magenta
Write-Host 'function Stop-AllServices { 
  param([int]$Timeout = 10)
  $jobs = Get-Job
  Write-Host "����ֹͣ $($jobs.Count) ������..." -ForegroundColor Yellow
  foreach ($job in $jobs) {
    Write-Host "ֹͣ��ҵ: $($job.Id) - $($job.Name)" -ForegroundColor Cyan
    try {
      Stop-Job -Id $job.Id -Timeout $Timeout -ErrorAction SilentlyContinue
      if ((Get-Job -Id $job.Id -ErrorAction SilentlyContinue).State -eq "Running") {
        Write-Host "ǿ��ֹͣ��ҵ: $($job.Id)" -ForegroundColor Red
        Remove-Job -Id $job.Id -Force -ErrorAction SilentlyContinue
      }
    } catch {
      Write-Host "����: $_" -ForegroundColor Red
    }
  }
  Write-Host "���з�����ֹͣ" -ForegroundColor Green
}
Stop-AllServices' -ForegroundColor White