# PowerShell 脚本：一键启动文书标注系统前端和后端
# 执行策略设置：如果遇到无法执行的问题，请先在管理员PowerShell中运行: Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

# 配置颜色和格式化输出
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
    Write-ColorOutput "       文书标注系统启动工具" "Cyan"
    Write-ColorOutput "=========================================" "Cyan"
    Write-Output ""
}

# 显示启动横幅
Show-Banner

# 配置路径和环境
$rootDir = Split-Path -Parent $PSScriptRoot
$frontendDir = Join-Path -Path $rootDir -ChildPath "frontend"
$backendDir = Join-Path -Path $rootDir -ChildPath "backend"

# 检查目录是否存在
if (-not (Test-Path -Path $frontendDir)) {
    Write-ColorOutput "错误：前端目录不存在 ($frontendDir)" "Red"
    exit 1
}

if (-not (Test-Path -Path $backendDir)) {
    Write-ColorOutput "错误：后端目录不存在 ($backendDir)" "Red"
    exit 1
}

# 激活 Conda 环境
Write-ColorOutput "正在激活 Conda 环境 (annotator)..." "Yellow"
conda activate annotator

# 检查 Conda 环境是否激活成功
if ($LASTEXITCODE -ne 0) {
    Write-ColorOutput "错误：无法激活 Conda 环境，请确保已安装 Conda 并创建了 'annotator' 环境" "Red"
    exit 1
}

# 启动后端服务
Write-ColorOutput "正在启动后端服务..." "Yellow"
$backendJob = Start-Job -ScriptBlock {
    param($dir)
    cd $dir
    python -m app.main
} -ArgumentList $backendDir

# 等待后端启动
Write-ColorOutput "等待后端服务启动 (5秒)..." "Yellow"
Start-Sleep -Seconds 5

# 检查后端是否成功启动
$backendState = Receive-Job -Job $backendJob -Keep
if ($null -eq $backendState) {
    Write-ColorOutput "后端服务启动中..." "Green"
} else {
    Write-ColorOutput "后端服务输出：" "Cyan"
    Write-Output $backendState
}

# 启动前端服务
Write-ColorOutput "正在启动前端服务..." "Yellow"
$frontendJob = Start-Job -ScriptBlock {
    param($dir)
    cd $dir
    npm run dev
} -ArgumentList $frontendDir

# 等待前端启动
Write-ColorOutput "等待前端服务启动 (5秒)..." "Yellow"
Start-Sleep -Seconds 5

# 检查前端是否成功启动
$frontendState = Receive-Job -Job $frontendJob -Keep
if ($null -eq $frontendState) {
    Write-ColorOutput "前端服务启动中..." "Green"
} else {
    Write-ColorOutput "前端服务输出：" "Cyan"
    Write-Output $frontendState
}

# 显示服务状态
Write-Output ""
Write-ColorOutput "=========================================" "Green"
Write-ColorOutput "       服务状态" "Green"
Write-ColorOutput "=========================================" "Green"
Write-ColorOutput "后端服务: 运行中 (http://localhost:8000)" "Green"
Write-ColorOutput "前端服务: 运行中 (http://localhost:3000)" "Green"
Write-ColorOutput "=========================================" "Green"
Write-Output ""
Write-ColorOutput "系统已启动! 请在浏览器中访问: http://localhost:3000" "Cyan"
Write-ColorOutput "按 Ctrl+C 停止所有服务" "Yellow"
Write-Output ""

# 等待用户按下 Ctrl+C
try {
    # 显示后端日志
    while ($true) {
        $backendOutput = Receive-Job -Job $backendJob -Keep
        if ($null -ne $backendOutput) {
            Write-ColorOutput "[后端] " "DarkGray" -NoNewline
            Write-Output $backendOutput
        }
        
        $frontendOutput = Receive-Job -Job $frontendJob -Keep
        if ($null -ne $frontendOutput) {
            Write-ColorOutput "[前端] " "DarkGray" -NoNewline
            Write-Output $frontendOutput
        }
        
        Start-Sleep -Seconds 1
    }
}
catch {
    # 当用户按 Ctrl+C 时
    Write-Output ""
    Write-ColorOutput "正在停止服务..." "Yellow"
    
    # 停止后端作业
    if ($null -ne $backendJob) {
        Stop-Job -Job $backendJob
        Remove-Job -Job $backendJob -Force
    }
    
    # 停止前端作业
    if ($null -ne $frontendJob) {
        Stop-Job -Job $frontendJob
        Remove-Job -Job $frontendJob -Force
    }
    
    Write-ColorOutput "所有服务已停止" "Green"
}
finally {
    # 清理所有残余作业
    Get-Job | Where-Object { $_.State -ne 'Completed' } | Stop-Job
    Get-Job | Remove-Job -Force
} 