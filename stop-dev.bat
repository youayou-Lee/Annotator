@echo off
chcp 65001 >nul
echo 🛑 停止文书标注系统开发环境...

REM 停止后端服务
echo 🔧 停止后端服务...
taskkill /f /im "python.exe" /fi "COMMANDLINE eq *uvicorn*" >nul 2>nul

REM 停止前端服务
echo 🔧 停止前端服务...
taskkill /f /im "node.exe" /fi "COMMANDLINE eq *vite*" >nul 2>nul

REM 停止cmd窗口
taskkill /f /fi "WINDOWTITLE eq Backend Server*" >nul 2>nul
taskkill /f /fi "WINDOWTITLE eq Frontend Server*" >nul 2>nul

echo.
echo 🎉 开发环境已停止！

pause 