@echo off
echo Starting Price Monitor Service...

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in PATH. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Install dependencies if not already installed
echo Installing/updating dependencies...
pip install -r requirements.txt

REM Start the FastAPI server
echo Starting FastAPI server...
uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause
