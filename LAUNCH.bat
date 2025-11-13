@echo off
REM Thai STT Auto-Tagger Launcher for Windows
REM Double-click this file to run the application

title Thai STT Auto-Tagger

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or later from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Run the launcher
python LAUNCH.py

REM If there was an error, keep window open
if errorlevel 1 (
    echo.
    echo An error occurred.
    pause
)
