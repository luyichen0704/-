@echo off
chcp 65001 >nul
echo ========================================
echo   基于大模型的自动化取证平台 - 一键安装
echo ========================================
echo.

:: 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [提示] 建议以管理员权限运行以获得最佳体验
    echo.
)

:: 1. 检查并安装Scoop
echo [1/5] 检查Scoop包管理器...
where scoop >nul 2>&1
if %errorLevel% neq 0 (
    echo 正在安装Scoop...
    powershell -ExecutionPolicy Bypass -Command "iwr -useb get.scoop.sh | iex"
    if %errorLevel% neq 0 (
        echo [错误] Scoop安装失败，请手动安装
        echo 访问: https://scoop.sh/
        pause
        exit /b 1
    )
    echo Scoop安装完成！
) else (
    echo Scoop已安装
)
echo.

:: 2. 添加Scoop仓库
echo [2/5] 配置Scoop仓库...
scoop bucket add extras 2>nul
scoop bucket add java 2>nul
echo 仓库配置完成
echo.

:: 3. 安装取证工具
echo [3/5] 安装取证工具...
echo.

echo --- 磁盘取证工具 ---
scoop install sleuthkit
echo.

echo --- 网络分析工具 ---
scoop install wireshark
echo.

echo --- 恶意代码分析 ---
scoop install yara
echo.

echo --- 密码破解工具 ---
scoop install hashcat
echo.

echo --- 文件处理工具 ---
scoop install 7zip ripgrep fd jq
echo.

echo --- 元数据工具 ---
scoop install exiftool
echo.

echo --- 音视频处理 ---
scoop install ffmpeg
echo.

echo --- 数据库工具 ---
scoop install sqlite
echo.

echo --- 加密工具 ---
scoop install openssl
echo.

echo --- Android分析 ---
scoop install jadx
echo.

echo --- 逆向工程 ---
scoop install radare2
echo.

echo --- 虚拟化工具 ---
scoop install qemu
echo.

:: 4. 安装Python包
echo [4/5] 安装Python依赖...
echo.

pip install --upgrade pip

echo --- AI核心依赖 ---
pip install aiohttp sentence-transformers
echo.

echo --- 取证工具绑定 ---
pip install volatility3 dissect-evidence pytsk3
echo.

echo --- 文档分析 ---
pip install oletools pycryptodome
echo.

echo --- 隐写分析 ---
pip install stegoveritas
echo.

echo --- 数据处理 ---
pip install pandas numpy chardet
echo.

echo --- Web框架 ---
pip install gradio fastapi uvicorn
echo.

:: 5. 安装Ruby (用于zsteg)
echo [5/5] 安装Ruby环境...
scoop install ruby
gem install zsteg
echo.

:: 完成
echo ========================================
echo   安装完成！
echo ========================================
echo.
echo 启动方式:
echo   1. 双击 start.bat 启动Web界面
echo   2. 或运行: python -m agent.core
echo.
echo 配置文件:
echo   编辑 config/llm_config.json 设置API密钥
echo.
pause
