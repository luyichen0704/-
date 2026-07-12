@echo off
chcp 65001 >nul
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
    echo 请手动删除项目文件夹
    pause
    exit /b 1
)

:: 启动卸载向导
start pythonw uninstaller_gui.py