# PowerShell �ű���һ�����������עϵͳǰ�˺ͺ��
# ִ�в������ã���������޷�ִ�е����⣬�����ڹ���ԱPowerShell������: Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

# ������ɫ�͸�ʽ�����
function Write-ColorOutput {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message,
        
        [Parameter(Mandatory = $true)]
        [string]$Color,
        
        [Parameter(Mandatory = $false)]
        [switch]$NoNewline
    )
    
    $originalColor = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $Color
    
    if ($NoNewline) {
        Write-Host $Message -NoNewline
    } else {
        Write-Output $Message
    }
    
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
try {
    Write-ColorOutput "���ڼ��� Conda ���� (annotator)..." "Yellow"
    conda activate annotator
    
    # ��� Conda �����Ƿ񼤻�ɹ�
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "�����޷����� Conda ��������ȷ���Ѱ�װ Conda �������� 'annotator' ����" "Red"
        exit 1
    }
} catch {
    Write-ColorOutput "�����޷����� Conda ����: $_" "Red"
    Write-ColorOutput "��ȷ���Ѱ�װ Conda �������� 'annotator' ����" "Red"
    exit 1
}

# ������˷���
Write-ColorOutput "����������˷���..." "Yellow"
$backendJob = Start-Job -ScriptBlock {
    param($dir)
    try {
        Set-Location $dir
        python -m app.main
    } catch {
        Write-Output "��˷�������ʧ��: $_"
        exit 1
    }
} -ArgumentList $backendDir

# �ȴ��������
Write-ColorOutput "�ȴ���˷������� (5��)..." "Yellow"
Start-Sleep -Seconds 5

# ������Ƿ�ɹ�����
$backendState = Receive-Job -Job $backendJob -Keep
$backendError = $false
if ($null -eq $backendState) {
    Write-ColorOutput "��˷���������..." "Green"
} elseif ($backendState -like "*��˷�������ʧ��*") {
    Write-ColorOutput "��˷�������ʧ�ܣ�" "Red"
    Write-ColorOutput $backendState "Red"
    $backendError = $true
} else {
    Write-ColorOutput "��˷��������" "Cyan"
    Write-Output $backendState
}

# ֻ�к��û���������ǰ��
if (-not $backendError) {
    # ����ǰ�˷���
    Write-ColorOutput "��������ǰ�˷���..." "Yellow"
    $frontendJob = Start-Job -ScriptBlock {
        param($dir)
        try {
            Set-Location $dir
            # ʹ�� ESM ģʽ���� Vite������ CJS ����
            $env:NODE_OPTIONS = "--conditions=development"
            npm run dev
        } catch {
            Write-Output "ǰ�˷�������ʧ��: $_"
            exit 1
        }
    } -ArgumentList $frontendDir

    # �ȴ�ǰ������
    Write-ColorOutput "�ȴ�ǰ�˷������� (8��)..." "Yellow"
    Start-Sleep -Seconds 8

    # ���ǰ���Ƿ�ɹ�����
    $frontendState = Receive-Job -Job $frontendJob -Keep
    $frontendError = $false
    if ($null -eq $frontendState) {
        Write-ColorOutput "ǰ�˷���������..." "Green"
    } elseif ($frontendState -like "*ǰ�˷�������ʧ��*") {
        Write-ColorOutput "ǰ�˷�������ʧ�ܣ�" "Red"
        Write-ColorOutput $frontendState "Red"
        $frontendError = $true
    } else {
        Write-ColorOutput "ǰ�˷��������" "Cyan"
        Write-Output $frontendState
    }

    # ��ʾ����״̬
    if (-not $frontendError) {
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

        # �������
        $openBrowser = Read-Host "�Ƿ��Զ����������(y/n)"
        if ($openBrowser -eq "y" -or $openBrowser -eq "Y") {
            Start-Process "http://localhost:3000"
        }

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
    } else {
        # ǰ������ʧ�ܣ�ֹͣ���
        if ($null -ne $backendJob) {
            Stop-Job -Job $backendJob
            Remove-Job -Job $backendJob -Force
            Write-ColorOutput "��ֹͣ��˷���" "Yellow"
        }
    }
} else {
    Write-ColorOutput "��������ʧ�ܣ�ǰ�˷���δ����" "Red"
}

# ȷ������������ҵ
finally {
    # �������в�����ҵ
    Get-Job | Where-Object { $_.State -ne 'Completed' } | Stop-Job
    Get-Job | Remove-Job -Force
} 