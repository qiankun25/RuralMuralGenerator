@echo off
echo ========================================
echo 乡村墙绘AI生成系统 - 环境设置
echo ========================================

cd /d "%~dp0.."

echo.
echo [1/5] 检查Python环境...
python --version
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo.
echo [2/5] 创建虚拟环境...
if exist "venv" (
    echo 虚拟环境已存在，跳过创建
) else (
    python -m venv venv
    echo 虚拟环境创建成功
)

echo.
echo [3/5] 激活虚拟环境...
call venv\Scripts\activate.bat

echo.
echo [4/5] 安装依赖包...
pip install -r requirements.txt

echo.
echo [5/5] 配置环境变量...
if not exist ".env" (
    copy .env.example .env
    echo 已创建.env文件，请编辑该文件填入API密钥
) else (
    echo .env文件已存在
)

echo.
echo ========================================
echo 环境设置完成！
echo ========================================
echo.
echo 下一步操作：
echo 1. 编辑 .env 文件，填入API密钥
echo 2. 运行 scripts\init_chromadb.bat 初始化知识库
echo 3. 运行 scripts\start_backend.bat 启动后端
echo 4. 运行 scripts\start_frontend.bat 启动前端
echo.
pause

