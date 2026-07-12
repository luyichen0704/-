@echo off
chcp 65001 >nul 2>nul
title Forensic AI Platform Installer
cd /d "%~dp0"

echo ========================================
echo   Forensic AI Platform Installer
echo ========================================
echo.
echo Checking Python...
echo.

:: Check Python
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ========================================
    echo   Python NOT FOUND!
    echo ========================================
    echo.
    echo Please install Python:
    echo 1. Go to: https://www.python.org/downloads/
    echo 2. Download Python 3.10 or newer
    echo 3. Run installer
    echo 4. IMPORTANT: Check "Add Python to PATH"!
    echo 5. Restart this installer
    echo.
    echo Opening download page...
    start https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python found:
python --version
echo.
echo Starting installer GUI...
echo.

python installer_gui.py

if %errorLevel% neq 0 (
    echo.
    echo ========================================
    echo   ERROR: Installer failed!
    echo ========================================
    echo.
    echo Try manual installation:
    echo 1. pip install -r requirements.txt
    echo 2. Run start.bat
    echo.
)

pause
