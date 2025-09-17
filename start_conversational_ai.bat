@echo off
echo.
echo =============================================
echo    🤖 Kokoro AI Conversational System
echo =============================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo ❌ Virtual environment not found!
    echo Please run the setup first.
    pause
    exit /b 1
)

echo 🔧 Starting Kokoro AI Conversational System...
echo.
echo Available interfaces:
echo   🌐 Web Interface: http://localhost:5002
echo   💬 CLI Chat: Run "python conversational_ai.py"
echo.
echo 💡 Press Ctrl+C to stop the server
echo.

REM Start the web interface
.venv\Scripts\python.exe conversational_web.py

pause