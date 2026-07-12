@echo off
chcp 65001 >nul 2>nul
title Installer
cd /d "%~dp0"

python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo Python not found! Please install Python 3.8+
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

python installer_gui.py
pause
