# GBK2312
# PowerShell 脚本：一键启动文书标注系统前端和后端
# 此脚本仅适用于人为调用，不适用AI调用。

# 配置颜色输出
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
# 获取当前脚本所在目录作为根目录
$rootDir = $PSScriptRoot
if (-not $rootDir) {
    $rootDir = (Get-Location).Path
}
Write-ColorOutput "项目根目录: $rootDir" "Yellow"

# 检查目录和启动脚本是否存在
$frontendDir = Join-Path -Path $rootDir -ChildPath "frontend"
$backendDir = Join-Path -Path $rootDir -ChildPath "backend" 
$frontendScriptPath = Join-Path -Path $rootDir -ChildPath "run-frontend.ps1"
$backendScriptPath = Join-Path -Path $rootDir -ChildPath "run-backend.ps1"

if (-not (Test-Path -Path $frontendDir)) {
    Write-ColorOutput "错误：前端目录不存在 ($frontendDir)" "Red"
    exit 1
}

if (-not (Test-Path -Path $backendDir)) {
    Write-ColorOutput "错误：后端目录不存在 ($backendDir)" "Red"
    exit 1
}

if (-not (Test-Path -Path $frontendScriptPath)) {
    Write-ColorOutput "错误：前端启动脚本不存在 ($frontendScriptPath)" "Red"
    exit 1
}

if (-not (Test-Path -Path $backendScriptPath)) {
    Write-ColorOutput "错误：后端启动脚本不存在 ($backendScriptPath)" "Red"
    exit 1
}

# 启动后端窗口
Write-ColorOutput "正在打开后端窗口..." "Yellow"
Start-Process powershell.exe -ArgumentList "-NoExit -ExecutionPolicy Bypass -File `"$backendScriptPath`"" -WindowStyle Normal

# 等待2秒，确保后端开始启动
Start-Sleep -Seconds 2

# 启动前端窗口
Write-ColorOutput "正在打开前端窗口..." "Yellow"
Start-Process powershell.exe -ArgumentList "-NoExit -ExecutionPolicy Bypass -File `"$frontendScriptPath`"" -WindowStyle Normal

# 显示打开浏览器的选项
Write-Output ""
Write-ColorOutput "服务启动中..." "Green"
Write-ColorOutput "前端地址: http://localhost:3000" "Cyan"
Write-ColorOutput "后端地址: http://localhost:8000" "Cyan"
Write-Output ""

# 等待启动完成
Start-Sleep -Seconds 3

Write-ColorOutput "启动完成！服务正在单独的窗口中运行。" "Green"
Write-ColorOutput "关闭相应的窗口即可停止对应服务。" "Yellow" 