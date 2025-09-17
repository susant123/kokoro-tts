@echo off
REM Kokoro TTS Easy Launcher
REM Usage: kokoro.bat input.txt [output.wav] [options]

set PYTHON_EXE=D:\00\kokoro\.venv\Scripts\python.exe

REM Check if virtual environment exists
if not exist "%PYTHON_EXE%" (
    echo Error: Virtual environment not found!
    echo Please run the setup script first.
    pause
    exit /b 1
)

REM Run Kokoro TTS with all passed arguments
"%PYTHON_EXE%" kokoro-tts %*
