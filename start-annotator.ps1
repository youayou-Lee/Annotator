# PowerShell 脚本：一键启动文书标注系统前端和后端
# 执行策略设置：如果遇到无法执行的问题，请先在管理员PowerShell中运行: Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

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

# 创建启动后端的脚本
$backendScript = @"
# 激活 Conda 环境
Write-Host "正在激活 Conda 环境 (annotator)..." -ForegroundColor Yellow
conda activate annotator

# 检查 Conda 环境是否激活成功
if (`$LASTEXITCODE -ne 0) {
    Write-Host "错误：无法激活 Conda 环境，请确保已安装 Conda 并创建了 'annotator' 环境" -ForegroundColor Red
    Read-Host "按任意键退出"
    exit 1
}

# 切换到后端目录
Set-Location "$backendDir"

# 启动后端服务
Write-Host "正在启动后端服务..." -ForegroundColor Green
Write-Host "后端服务地址: http://localhost:8000" -ForegroundColor Cyan
Write-Host "按 Ctrl+C 可以停止服务" -ForegroundColor Yellow
Write-Host "=================================" -ForegroundColor Green

# 执行后端启动命令
python -m app.main

# 等待用户输入后关闭窗口
Read-Host "按任意键退出"
"@

# 创建启动前端的脚本
$frontendScript = @"
# 切换到前端目录
Set-Location "$frontendDir"

# 设置环境变量，消除 CJS 警告
`$env:NODE_OPTIONS="--no-warnings"

# 启动前端服务
Write-Host "正在启动前端服务..." -ForegroundColor Green
Write-Host "前端服务地址: http://localhost:3000" -ForegroundColor Cyan
Write-Host "按 Ctrl+C 可以停止服务" -ForegroundColor Yellow
Write-Host "=================================" -ForegroundColor Green

# 执行前端启动命令
npm run dev

# 等待用户输入后关闭窗口
Read-Host "按任意键退出"
"@

# 保存临时脚本
$backendScriptPath = Join-Path -Path $env:TEMP -ChildPath "run-backend.ps1"
$frontendScriptPath = Join-Path -Path $env:TEMP -ChildPath "run-frontend.ps1"

$backendScript | Out-File -FilePath $backendScriptPath -Encoding utf8
$frontendScript | Out-File -FilePath $frontendScriptPath -Encoding utf8

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

# 询问是否打开浏览器
$openBrowser = Read-Host "是否自动打开浏览器？(y/n)"
if ($openBrowser -eq "y" -or $openBrowser -eq "Y") {
    Start-Process "http://localhost:3000"
}

# 等待一段时间后删除临时脚本
Start-Sleep -Seconds 5
if (Test-Path $backendScriptPath) {
    Remove-Item $backendScriptPath -Force -ErrorAction SilentlyContinue
}
if (Test-Path $frontendScriptPath) {
    Remove-Item $frontendScriptPath -Force -ErrorAction SilentlyContinue
}

Write-ColorOutput "启动完成！服务正在单独的窗口中运行。" "Green"
Write-ColorOutput "关闭相应的窗口即可停止对应服务。" "Yellow" 