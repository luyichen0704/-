@echo off
chcp 65001 >nul
echo ========================================
echo   基于大模型的自动化取证平台
echo ========================================
echo.

:: 检查Python
where python >nul 2>&1
if %errorLevel% neq 0 (
    echo [错误] 未找到Python，请先安装Python 3.8+
    echo 下载: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 检查依赖
echo [1/3] 检查依赖...
pip show aiohttp >nul 2>&1
if %errorLevel% neq 0 (
    echo 正在安装依赖...
    pip install -r requirements.txt
)
echo 依赖检查完成
echo.

:: 检查配置
echo [2/3] 检查配置...
if not exist "config\llm_config.json" (
    echo [提示] 未找到配置文件，正在创建默认配置...
    copy config\llm_config.example.json config\llm_config.json
    echo 请编辑 config\llm_config.json 设置API密钥
    echo.
)

:: 启动服务
echo [3/3] 启动服务...
echo.
echo 访问地址: http://localhost:7860
echo 按 Ctrl+C 停止服务
echo.

python -m openwebui.pipeline

pause
