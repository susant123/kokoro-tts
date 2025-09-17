@echo off
echo.
echo ===============================================
echo   WARNING: Kokoro TTS Python 3.13 Compatibility Fix
echo ===============================================
echo.
echo This script helps run Kokoro TTS with Python 3.13
echo Note: Some features may not work due to compatibility issues
echo.

REM Check if Python 3.12 environment exists
if exist ".venv312\Scripts\python.exe" (
    echo SUCCESS: Using Python 3.12 environment
    set PYTHON_EXE=.venv312\Scripts\python.exe
) else (
    echo WARNING: Python 3.12 environment not found, falling back to Python 3.13
    echo Note: Compatibility issues expected with Python 3.13
    set PYTHON_EXE=.venv\Scripts\python.exe
)

REM Run with the appropriate Python version
echo Starting Kokoro TTS Web Frontend...
"%PYTHON_EXE%" app.py

pause
