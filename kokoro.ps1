# Kokoro TTS PowerShell Launcher
# Usage: .\kokoro.ps1 input.txt [output.wav] [options]

$pythonExe = "D:\00\kokoro\.venv\Scripts\python.exe"

# Check if virtual environment exists
if (!(Test-Path $pythonExe)) {
    Write-Error "Virtual environment not found! Please run the setup script first."
    exit 1
}

# Run Kokoro TTS with all passed arguments
& $pythonExe kokoro-tts @args
