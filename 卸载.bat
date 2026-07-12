@echo off
chcp 65001 >nul
title 取证AI平台 - 卸载程序
cd /d "%~dp0"

echo ========================================
echo   取证AI平台 - 卸载程序
echo ========================================
echo.
echo 正在启动卸载向导...
echo.

:: 检查Python
where python >nul 2>&1
if %errorLevel% neq 0 (
    echo [错误] 未找到Python
    echo.
    echo 请手动删除项目文件夹
    echo.
    pause
    exit /b 1
)

:: 启动卸载向导
python uninstaller_gui.py

if %errorLevel% neq 0 (
    echo.
    echo [错误] 卸载程序异常退出
    pause
)