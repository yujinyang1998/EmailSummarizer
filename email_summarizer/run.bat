@echo off
title PDF Email Summarizer

echo =============================
echo   PDF Email Summarizer
echo =============================
echo.

:: Check if virtual environment exists
if not exist "venv" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup.bat first.
    pause
    exit /b 1
)

:: Activate virtual environment
echo [INFO] Starting application...
call venv\Scripts\activate.bat

:: Start the Flask application
echo.
echo Open your browser and go to: http://localhost:5000
echo Press Ctrl+C to stop the application
echo.
python app.py
