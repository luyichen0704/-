@echo off
chcp 65001 >nul
echo ========================================
echo   创建桌面快捷方式
echo ========================================
echo.

:: 运行PowerShell脚本
powershell -ExecutionPolicy Bypass -File "%~dp0create_shortcut.ps1"

echo.
pause