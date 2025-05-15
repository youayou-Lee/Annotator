# PowerShell 脚本：一键启动文书标注系统前端和后端
# 执行策略设置：如果遇到无法执行的问题，请先在管理员PowerShell中运行: Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

# 配置颜色和格式化输出
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
    Write-ColorOutput "       文书标注系统启动工具" "Cyan"
    Write-ColorOutput "=========================================" "Cyan"
    Write-Output ""
}

# 显示启动横幅
Show-Banner

# 配置路径和环境
# 获取当前脚本所在目录作为根目录
$rootDir = $PSScriptRoot
if (-not $rootDir) {
    $rootDir = (Get-Location).Path
}
Write-ColorOutput "项目根目录: $rootDir" "Yellow"
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
try {
    Write-ColorOutput "正在激活 Conda 环境 (annotator)..." "Yellow"
    conda activate annotator
    
    # 检查 Conda 环境是否激活成功
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "错误：无法激活 Conda 环境，请确保已安装 Conda 并创建了 'annotator' 环境" "Red"
        exit 1
    }
} catch {
    Write-ColorOutput "错误：无法激活 Conda 环境: $_" "Red"
    Write-ColorOutput "请确保已安装 Conda 并创建了 'annotator' 环境" "Red"
    exit 1
}

# 启动后端服务
Write-ColorOutput "正在启动后端服务..." "Yellow"
$backendJob = Start-Job -ScriptBlock {
    param($dir)
    try {
        Set-Location $dir
        python -m app.main
    } catch {
        Write-Output "后端服务启动失败: $_"
        exit 1
    }
} -ArgumentList $backendDir

# 等待后端启动
Write-ColorOutput "等待后端服务启动 (5秒)..." "Yellow"
Start-Sleep -Seconds 5

# 检查后端是否成功启动
$backendState = Receive-Job -Job $backendJob -Keep
$backendError = $false
if ($null -eq $backendState) {
    Write-ColorOutput "后端服务启动中..." "Green"
} elseif ($backendState -like "*后端服务启动失败*") {
    Write-ColorOutput "后端服务启动失败！" "Red"
    Write-ColorOutput $backendState "Red"
    $backendError = $true
} else {
    Write-ColorOutput "后端服务输出：" "Cyan"
    Write-Output $backendState
}

# 只有后端没问题才启动前端
if (-not $backendError) {
    # 启动前端服务
    Write-ColorOutput "正在启动前端服务..." "Yellow"
    $frontendJob = Start-Job -ScriptBlock {
        param($dir)
        try {
            Set-Location $dir
            # 使用 ESM 模式启动 Vite，避免 CJS 警告
            $env:NODE_OPTIONS = "--conditions=development"
            npm run dev
        } catch {
            Write-Output "前端服务启动失败: $_"
            exit 1
        }
    } -ArgumentList $frontendDir

    # 等待前端启动
    Write-ColorOutput "等待前端服务启动 (8秒)..." "Yellow"
    Start-Sleep -Seconds 8

    # 检查前端是否成功启动
    $frontendState = Receive-Job -Job $frontendJob -Keep
    $frontendError = $false
    if ($null -eq $frontendState) {
        Write-ColorOutput "前端服务启动中..." "Green"
    } elseif ($frontendState -like "*前端服务启动失败*") {
        Write-ColorOutput "前端服务启动失败！" "Red"
        Write-ColorOutput $frontendState "Red"
        $frontendError = $true
    } else {
        Write-ColorOutput "前端服务输出：" "Cyan"
        Write-Output $frontendState
    }

    # 显示服务状态
    if (-not $frontendError) {
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

        # 打开浏览器
        $openBrowser = Read-Host "是否自动打开浏览器？(y/n)"
        if ($openBrowser -eq "y" -or $openBrowser -eq "Y") {
            Start-Process "http://localhost:3000"
        }

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
    } else {
        # 前端启动失败，停止后端
        if ($null -ne $backendJob) {
            Stop-Job -Job $backendJob
            Remove-Job -Job $backendJob -Force
            Write-ColorOutput "已停止后端服务" "Yellow"
        }
    }
} else {
    Write-ColorOutput "因后端启动失败，前端服务未启动" "Red"
}

# 确保清理所有作业
finally {
    # 清理所有残余作业
    Get-Job | Where-Object { $_.State -ne 'Completed' } | Stop-Job
    Get-Job | Remove-Job -Force
} 