# PowerShell �ű���һ�����������עϵͳǰ�˺ͺ��
# ִ�в������ã���������޷�ִ�е����⣬�����ڹ���ԱPowerShell������: Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

# ������ɫ�͸�ʽ�����
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

# ���� Conda ����
Write-ColorOutput "���ڼ��� Conda ���� (annotator)..." "Yellow"
conda activate annotator

# ��� Conda �����Ƿ񼤻�ɹ�
if ($LASTEXITCODE -ne 0) {
    Write-ColorOutput "�����޷����� Conda ��������ȷ���Ѱ�װ Conda �������� 'annotator' ����" "Red"
    exit 1
}

# ������˷���
Write-ColorOutput "����������˷���..." "Yellow"
$backendJob = Start-Job -ScriptBlock {
    param($dir)
    cd $dir
    python -m app.main
} -ArgumentList $backendDir

# �ȴ��������
Write-ColorOutput "�ȴ���˷������� (5��)..." "Yellow"
Start-Sleep -Seconds 5

# ������Ƿ�ɹ�����
$backendState = Receive-Job -Job $backendJob -Keep
if ($null -eq $backendState) {
    Write-ColorOutput "��˷���������..." "Green"
} else {
    Write-ColorOutput "��˷��������" "Cyan"
    Write-Output $backendState
}

# ����ǰ�˷���
Write-ColorOutput "��������ǰ�˷���..." "Yellow"
$frontendJob = Start-Job -ScriptBlock {
    param($dir)
    cd $dir
    npm run dev
} -ArgumentList $frontendDir

# �ȴ�ǰ������
Write-ColorOutput "�ȴ�ǰ�˷������� (5��)..." "Yellow"
Start-Sleep -Seconds 5

# ���ǰ���Ƿ�ɹ�����
$frontendState = Receive-Job -Job $frontendJob -Keep
if ($null -eq $frontendState) {
    Write-ColorOutput "ǰ�˷���������..." "Green"
} else {
    Write-ColorOutput "ǰ�˷��������" "Cyan"
    Write-Output $frontendState
}

# ��ʾ����״̬
Write-Output ""
Write-ColorOutput "=========================================" "Green"
Write-ColorOutput "       ����״̬" "Green"
Write-ColorOutput "=========================================" "Green"
Write-ColorOutput "��˷���: ������ (http://localhost:8000)" "Green"
Write-ColorOutput "ǰ�˷���: ������ (http://localhost:3000)" "Green"
Write-ColorOutput "=========================================" "Green"
Write-Output ""
Write-ColorOutput "ϵͳ������! ����������з���: http://localhost:3000" "Cyan"
Write-ColorOutput "�� Ctrl+C ֹͣ���з���" "Yellow"
Write-Output ""

# �ȴ��û����� Ctrl+C
try {
    # ��ʾ�����־
    while ($true) {
        $backendOutput = Receive-Job -Job $backendJob -Keep
        if ($null -ne $backendOutput) {
            Write-ColorOutput "[���] " "DarkGray" -NoNewline
            Write-Output $backendOutput
        }
        
        $frontendOutput = Receive-Job -Job $frontendJob -Keep
        if ($null -ne $frontendOutput) {
            Write-ColorOutput "[ǰ��] " "DarkGray" -NoNewline
            Write-Output $frontendOutput
        }
        
        Start-Sleep -Seconds 1
    }
}
catch {
    # ���û��� Ctrl+C ʱ
    Write-Output ""
    Write-ColorOutput "����ֹͣ����..." "Yellow"
    
    # ֹͣ�����ҵ
    if ($null -ne $backendJob) {
        Stop-Job -Job $backendJob
        Remove-Job -Job $backendJob -Force
    }
    
    # ֹͣǰ����ҵ
    if ($null -ne $frontendJob) {
        Stop-Job -Job $frontendJob
        Remove-Job -Job $frontendJob -Force
    }
    
    Write-ColorOutput "���з�����ֹͣ" "Green"
}
finally {
    # �������в�����ҵ
    Get-Job | Where-Object { $_.State -ne 'Completed' } | Stop-Job
    Get-Job | Remove-Job -Force
} 