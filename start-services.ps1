# ��̨��������ű�-�˽ű�������AI���á�
# GBK2312

Write-Host "����׼����������..." -ForegroundColor Cyan

# ����������ҵ
Write-Host "����������ҵ..." -ForegroundColor Yellow
Get-Job | Where-Object { $_.State -eq "Running" } | Stop-Job
Get-Job | Remove-Job

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
Write-Host "Stop-Job -Id $($backendJob.Id); Stop-Job -Id $($frontendJob.Id)" -ForegroundColor White