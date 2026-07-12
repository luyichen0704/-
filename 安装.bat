@echo off
chcp 65001 >nul
title 取证AI平台 - 安装程序
cd /d "%~dp0"

echo ========================================
echo   取证AI平台 - 安装程序
echo ========================================
echo.
echo 正在启动安装向导...
echo.

:: 检查Python
where python >nul 2>&1
if %errorLevel% neq 0 (
    echo [错误] 未找到Python
    echo.
    echo 请先安装Python 3.8+:
    echo https://www.python.org/downloads/
    echo.
    echo 安装时请勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

:: 显示Python版本
python --version
echo.

:: 检查installer_gui.py是否存在
if not exist "installer_gui.py" (
    echo [错误] 未找到 installer_gui.py
    echo 请确保在正确的目录运行此脚本
    pause
    exit /b 1
)

:: 启动安装向导
echo 正在启动安装界面...
echo.
python installer_gui.py

:: 如果退出码不为0，显示错误
if %errorLevel% neq 0 (
    echo.
    echo [错误] 安装程序异常退出
    echo 错误代码: %errorLevel%
    echo.
    pause
)