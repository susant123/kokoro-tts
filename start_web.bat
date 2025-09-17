@echo off
echo.
echo =============================================
echo    🎤 Kokoro TTS Web Frontend Launcher
echo =============================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo ❌ Virtual environment not found!
    echo Please run the setup first.
    pause
    exit /b 1
)

echo 🔧 Starting Kokoro TTS Web Server...
echo 📡 The web interface will be available at:
echo    http://localhost:5000
echo.
echo 💡 Press Ctrl+C to stop the server
echo.

REM Start the Flask application
.venv\Scripts\python.exe app.py

pause
