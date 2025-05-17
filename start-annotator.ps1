# GBK2312
# PowerShell �ű���һ�����������עϵͳǰ�˺ͺ��
# �˽ű�����������Ϊ���ã�������AI���á�

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

# ���Ŀ¼�������ű��Ƿ����
$frontendDir = Join-Path -Path $rootDir -ChildPath "frontend"
$backendDir = Join-Path -Path $rootDir -ChildPath "backend" 
$frontendScriptPath = Join-Path -Path $rootDir -ChildPath "run-frontend.ps1"
$backendScriptPath = Join-Path -Path $rootDir -ChildPath "run-backend.ps1"

if (-not (Test-Path -Path $frontendDir)) {
    Write-ColorOutput "����ǰ��Ŀ¼������ ($frontendDir)" "Red"
    exit 1
}

if (-not (Test-Path -Path $backendDir)) {
    Write-ColorOutput "���󣺺��Ŀ¼������ ($backendDir)" "Red"
    exit 1
}

if (-not (Test-Path -Path $frontendScriptPath)) {
    Write-ColorOutput "����ǰ�������ű������� ($frontendScriptPath)" "Red"
    exit 1
}

if (-not (Test-Path -Path $backendScriptPath)) {
    Write-ColorOutput "���󣺺�������ű������� ($backendScriptPath)" "Red"
    exit 1
}

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

Write-ColorOutput "������ɣ��������ڵ����Ĵ��������С�" "Green"
Write-ColorOutput "�ر���Ӧ�Ĵ��ڼ���ֹͣ��Ӧ����" "Yellow" 