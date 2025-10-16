@echo off
echo ========================================
echo 初始化ChromaDB知识库
echo ========================================

cd /d "%~dp0.."

if not exist "venv\Scripts\activate.bat" (
    echo 错误: 未找到虚拟环境，请先运行 setup.bat
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo 正在初始化ChromaDB...
python scripts\init_chromadb.py

pause

