@echo off
echo Starting Apon AI - Grocery Price Monitor
echo ===================================

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Node.js is not installed or not in PATH
    pause
    exit /b 1
)

REM Create and activate virtual environment
echo.
echo Setting up Python virtual environment...
if not exist .venv (
    python -m venv .venv
)
call .venv\Scripts\activate

REM Install Python dependencies
echo.
echo Installing Python dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Error installing Python dependencies
    pause
    exit /b 1
)

REM Install Node.js dependencies
echo.
echo Installing Node.js dependencies...
cd apps\web
call npm install
if %ERRORLEVEL% neq 0 (
    echo Error installing Node.js dependencies
    pause
    exit /b 1
)
cd ..\..

echo.
echo Installation complete! Starting the application...
echo.

REM Start the application
start "" cmd /k "python run.py"

echo Application started! Check the new console window for details.
echo You can access the application at: http://localhost:3000
echo.
pause
