# PowerShell �ű���һ�����������עϵͳǰ�˺ͺ��
# ִ�в������ã���������޷�ִ�е����⣬�����ڹ���ԱPowerShell������: Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

# ������ɫ���
function Write-ColorOutput {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message,
        
        [Parameter(Mandatory = $true)]
        [string]$Color
    )
    
    $originalColor = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $Color
    Write-Output $Message
    $host.UI.RawUI.ForegroundColor = $originalColor
}

function Show-Banner {
    Write-Output ""
    Write-ColorOutput "=========================================" "Cyan"
    Write-ColorOutput "       �����עϵͳ��������" "Cyan"
    Write-ColorOutput "=========================================" "Cyan"
    Write-Output ""
}

# ��ʾ�������
Show-Banner

# ����·���ͻ���
# ��ȡ��ǰ�ű�����Ŀ¼��Ϊ��Ŀ¼
$rootDir = $PSScriptRoot
if (-not $rootDir) {
    $rootDir = (Get-Location).Path
}
Write-ColorOutput "��Ŀ��Ŀ¼: $rootDir" "Yellow"
$frontendDir = Join-Path -Path $rootDir -ChildPath "frontend"
$backendDir = Join-Path -Path $rootDir -ChildPath "backend"

# ���Ŀ¼�Ƿ����
if (-not (Test-Path -Path $frontendDir)) {
    Write-ColorOutput "����ǰ��Ŀ¼������ ($frontendDir)" "Red"
    exit 1
}

if (-not (Test-Path -Path $backendDir)) {
    Write-ColorOutput "���󣺺��Ŀ¼������ ($backendDir)" "Red"
    exit 1
}

# ����������˵Ľű�
$backendScript = @"
# ���� Conda ����
Write-Host "���ڼ��� Conda ���� (annotator)..." -ForegroundColor Yellow
conda activate annotator

# ��� Conda �����Ƿ񼤻�ɹ�
if (`$LASTEXITCODE -ne 0) {
    Write-Host "�����޷����� Conda ��������ȷ���Ѱ�װ Conda �������� 'annotator' ����" -ForegroundColor Red
    Read-Host "��������˳�"
    exit 1
}

# �л������Ŀ¼
Set-Location "$backendDir"

# ������˷���
Write-Host "����������˷���..." -ForegroundColor Green
Write-Host "��˷����ַ: http://localhost:8000" -ForegroundColor Cyan
Write-Host "�� Ctrl+C ����ֹͣ����" -ForegroundColor Yellow
Write-Host "=================================" -ForegroundColor Green

# ִ�к����������
python -m app.main

# �ȴ��û������رմ���
Read-Host "��������˳�"
"@

# ��������ǰ�˵Ľű�
$frontendScript = @"
# �л���ǰ��Ŀ¼
Set-Location "$frontendDir"

# ���û������������� CJS ����
`$env:NODE_OPTIONS="--no-warnings"

# ����ǰ�˷���
Write-Host "��������ǰ�˷���..." -ForegroundColor Green
Write-Host "ǰ�˷����ַ: http://localhost:3000" -ForegroundColor Cyan
Write-Host "�� Ctrl+C ����ֹͣ����" -ForegroundColor Yellow
Write-Host "=================================" -ForegroundColor Green

# ִ��ǰ����������
npm run dev

# �ȴ��û������رմ���
Read-Host "��������˳�"
"@

# ������ʱ�ű�
$backendScriptPath = Join-Path -Path $env:TEMP -ChildPath "run-backend.ps1"
$frontendScriptPath = Join-Path -Path $env:TEMP -ChildPath "run-frontend.ps1"

$backendScript | Out-File -FilePath $backendScriptPath -Encoding utf8
$frontendScript | Out-File -FilePath $frontendScriptPath -Encoding utf8

# ������˴���
Write-ColorOutput "���ڴ򿪺�˴���..." "Yellow"
Start-Process powershell.exe -ArgumentList "-NoExit -ExecutionPolicy Bypass -File `"$backendScriptPath`"" -WindowStyle Normal

# �ȴ�2�룬ȷ����˿�ʼ����
Start-Sleep -Seconds 2

# ����ǰ�˴���
Write-ColorOutput "���ڴ�ǰ�˴���..." "Yellow"
Start-Process powershell.exe -ArgumentList "-NoExit -ExecutionPolicy Bypass -File `"$frontendScriptPath`"" -WindowStyle Normal

# ��ʾ���������ѡ��
Write-Output ""
Write-ColorOutput "����������..." "Green"
Write-ColorOutput "ǰ�˵�ַ: http://localhost:3000" "Cyan"
Write-ColorOutput "��˵�ַ: http://localhost:8000" "Cyan"
Write-Output ""

# �ȴ��������
Start-Sleep -Seconds 3

# ѯ���Ƿ�������
$openBrowser = Read-Host "�Ƿ��Զ����������(y/n)"
if ($openBrowser -eq "y" -or $openBrowser -eq "Y") {
    Start-Process "http://localhost:3000"
}

# �ȴ�һ��ʱ���ɾ����ʱ�ű�
Start-Sleep -Seconds 5
if (Test-Path $backendScriptPath) {
    Remove-Item $backendScriptPath -Force -ErrorAction SilentlyContinue
}
if (Test-Path $frontendScriptPath) {
    Remove-Item $frontendScriptPath -Force -ErrorAction SilentlyContinue
}

Write-ColorOutput "������ɣ��������ڵ����Ĵ��������С�" "Green"
Write-ColorOutput "�ر���Ӧ�Ĵ��ڼ���ֹͣ��Ӧ����" "Yellow" 