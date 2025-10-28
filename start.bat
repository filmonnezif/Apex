@echo off
echo Starting Nestle UAE Price Optimization Platform...
echo.

REM Start backend
echo Starting FastAPI Backend...
cd backend
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate
pip install -r requirements.txt >nul 2>&1
start /B python main.py
echo Backend started
cd ..

REM Wait a bit
timeout /t 3 /nobreak >nul

REM Start frontend
echo Starting Nuxt Frontend...
cd frontend
if not exist node_modules (
    echo Installing dependencies...
    call npm install
)
start /B npm run dev
echo Frontend started
cd ..

echo.
echo ================================================
echo    Nestle UAE Price Optimization Platform
echo ================================================
echo.
echo   Frontend:  http://localhost:3000
echo   Backend:   http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo.
echo ================================================
echo.
echo Press Ctrl+C to stop all services
pause
