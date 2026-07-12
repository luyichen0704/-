@echo off
chcp 65001 >nul
echo ========================================
echo   基于大模型的自动化取证平台
echo ========================================
echo.
echo 请选择启动模式:
echo.
echo [1] Web UI 界面 (推荐)
echo [2] API 服务
echo [3] 同时启动 Web UI 和 API
echo [0] 退出
echo.
set /p choice=请输入选项: 

if "%choice%"=="1" goto webui
if "%choice%"=="2" goto api
if "%choice%"=="3" goto both
if "%choice%"=="0" goto end
echo 无效选项，请重新运行
pause
exit /b 1

:webui
echo.
echo 启动 Web UI...
echo 访问地址: http://localhost:7860
echo.
python -m web.app
goto end

:api
echo.
echo 启动 API 服务...
echo API文档: http://localhost:8000/docs
echo.
python -m api.main
goto end

:both
echo.
echo 启动 Web UI 和 API 服务...
echo Web UI: http://localhost:7860
echo API文档: http://localhost:8000
echo.
start "API Service" python -m api.main
timeout /t 3 >nul
python -m web.app
goto end

:end
pause
