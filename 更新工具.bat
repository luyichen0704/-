@echo off
chcp 65001 >nul
title 取证AI平台 - 更新工具
cd /d "%~dp0"

echo ========================================
echo   取证AI平台 - 更新工具
echo ========================================
echo.

:: 检查Python
where python >nul 2>&1
if %errorLevel% neq 0 (
    echo [错误] 未找到Python
    pause
    exit /b 1
)

:: 启动更新工具
python updater_gui.py

if %errorLevel% neq 0 (
    echo.
    echo [错误] 更新工具异常退出
    pause
)