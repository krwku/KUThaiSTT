@echo off
REM Annotation GUI Launcher for Windows
REM Double-click to open the annotation interface

title Thai STT Annotation GUI

echo.
echo ========================================
echo Thai STT Annotation GUI
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed
    echo.
    echo Please install Python 3.8+ from:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Check if metadata directory exists
if not exist "metadata" (
    echo WARNING: 'metadata' directory not found
    echo.
    echo Please process audio files first to generate metadata.
    echo Run: LAUNCH.bat and select option 1 or 2
    echo.
    pause
    exit /b 1
)

REM Check for pygame (optional)
python -c "import pygame" 2>nul
if errorlevel 1 (
    echo.
    echo NOTE: pygame not installed - audio playback will be disabled
    echo To enable audio playback, run:
    echo    pip install pygame
    echo.
    echo Continuing without audio playback...
    timeout /t 3
)

echo Starting Annotation GUI...
echo.

REM Run the GUI
python annotation_gui.py

REM If there was an error
if errorlevel 1 (
    echo.
    echo An error occurred while running the GUI.
    echo.
    echo Common solutions:
    echo  1. Make sure annotation_gui.py is in the current directory
    echo  2. Install required packages: pip install -r requirements.txt
    echo  3. Check the error message above for details
    echo.
    pause
)
