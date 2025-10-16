@echo off
echo ========================================
echo 启动后端服务 (FastAPI)
echo ========================================

cd backend
python -m uvicorn main:app --reload --port 8000

pause

