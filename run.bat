@echo off
setlocal enabledelayedexpansion

echo =======================================================
echo         CareerCompass AI - Windows Launcher
echo =======================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python was not found in your system PATH.
    echo Please install Python 3.10 or higher from https://www.python.org/downloads/
    echo During installation, be sure to check "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

:: Create virtual environment if it does not exist
if not exist "venv\Scripts\activate.bat" (
    echo [*] Creating Python virtual environment in 'venv'...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: Activate virtual environment
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat

:: Install or update dependencies
echo [*] Checking dependencies from requirements.txt...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [WARNING] Some dependencies had warnings during install. Proceeding...
)

:: Open web browser after a short pause
start "" http://127.0.0.1:5000

:: Start the Flask web application
echo.
echo =======================================================
echo  CareerCompass AI is starting!
echo  Local URL: http://127.0.0.1:5000
echo  Press Ctrl+C in this window to stop the server.
echo =======================================================
echo.

python app.py

pause
