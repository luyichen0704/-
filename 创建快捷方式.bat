@echo off
chcp 65001 >nul
title 创建桌面快捷方式
cd /d "%~dp0"

echo ========================================
echo   创建桌面快捷方式
echo ========================================
echo.

:: 运行PowerShell脚本
powershell -ExecutionPolicy Bypass -File "create_shortcut.ps1"

echo.
pause