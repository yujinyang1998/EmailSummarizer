@echo off
title PDF Email Summarizer Setup

echo ==========================================
echo   PDF Email Summarizer - Windows Setup  
echo ==========================================
echo.

echo [INFO] Starting setup process...

:: Check if Python is installed
echo [INFO] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

:: Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [SUCCESS] Found Python %PYTHON_VERSION%

:: Create virtual environment
echo [INFO] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)

:: Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

:: Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

:: Install requirements
echo [INFO] Installing requirements...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install requirements
    pause
    exit /b 1
)

:: Create .env file if it doesn't exist
if not exist .env (
    echo [INFO] Creating .env file...
    copy .env_example .env
    echo [INFO] Please edit .env file to add your OpenAI API key (optional)
)

:: Create uploads directory
if not exist uploads mkdir uploads

echo.
echo [SUCCESS] Setup completed successfully!
echo.
echo [INFO] To start the application:
echo   1. Run: run.bat
echo   2. Or manually:
echo      - venv\Scripts\activate.bat
echo      - python app.py
echo   3. Open browser to: http://localhost:5000
echo.
pause
