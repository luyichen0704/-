@echo off
chcp 65001 >nul 2>nul
title Updater
cd /d "%~dp0"

python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo Python not found!
    pause
    exit /b 1
)

python updater_gui.py
pause
