@echo off
chcp 65001 >nul 2>nul
title Uninstaller
cd /d "%~dp0"

python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo Python not found!
    echo Please delete the folder manually.
    pause
    exit /b 1
)

python uninstaller_gui.py
pause
