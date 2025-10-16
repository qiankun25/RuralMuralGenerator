@echo off
echo ========================================
echo 运行测试
echo ========================================

cd /d "%~dp0.."

if not exist "venv\Scripts\activate.bat" (
    echo 错误: 未找到虚拟环境，请先运行 setup.bat
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo.
echo [1/3] 测试服务层...
python tests\test_services.py

echo.
echo [2/3] 测试智能体...
python tests\test_agents.py

echo.
echo [3/3] 运行pytest...
pytest tests\ -v

echo.
echo ========================================
echo 测试完成
echo ========================================
pause

