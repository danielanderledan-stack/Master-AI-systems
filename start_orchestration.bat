@echo off
REM Start script for Master AI Orchestration System (Windows)

echo ============================================================================
echo           Master AI Orchestration System - Starting...
echo ============================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python is not installed. Please install Python 3.11 or later.
    exit /b 1
)

echo OK Python found
python --version

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo Installing dependencies...
pip install -r requirements.txt --quiet

REM Check if orchestration_config.json exists
if not exist "orchestration_config.json" (
    echo X orchestration_config.json not found!
    exit /b 1
)

echo OK Configuration file found

REM Start the server
echo.
echo Starting API server on http://localhost:8000
echo API documentation available at http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python api_server.py
