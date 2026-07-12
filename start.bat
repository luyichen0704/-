@echo off
chcp 65001 >nul
title 取证AI平台 - 启动
cd /d "%~dp0"

echo ========================================
echo   取证AI平台
echo ========================================
echo.

:: 检查Python
where python >nul 2>&1
if %errorLevel% neq 0 (
    echo [错误] 未找到Python
    echo 请先安装Python 3.8+
    pause
    exit /b 1
)

:: 检查配置文件
if not exist "config\llm_config.json" (
    echo [提示] 未找到API配置文件
    echo 正在创建默认配置...
    if exist "config\llm_config.example.json" (
        copy "config\llm_config.example.json" "config\llm_config.json" >nul
        echo 已创建 config\llm_config.json
        echo 请编辑此文件填入API密钥
        echo.
    )
)

:: 启动Web界面
echo 正在启动Web界面...
echo 访问地址: http://localhost:7860
echo 按 Ctrl+C 停止服务
echo.
python -m web.app

pause