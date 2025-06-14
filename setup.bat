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

    echo Open your browser and go to: http://localhost:5000
    echo Press Ctrl+C to stop the application
    echo.
    python run.py
) else (
    %INFO% Setup complete! To run later:
    echo   1. venv\Scripts\activate.bat
    echo   2. python run.py
    echo.
    pause
)
