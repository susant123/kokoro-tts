# Kokoro TTS Web Frontend Launcher (PowerShell)

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "   🎤 Kokoro TTS Web Frontend Launcher" -ForegroundColor Yellow
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (!(Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run the setup first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "🔧 Starting Kokoro TTS Web Server..." -ForegroundColor Green
Write-Host "📡 The web interface will be available at:" -ForegroundColor Cyan
Write-Host "   http://localhost:5000" -ForegroundColor White
Write-Host ""
Write-Host "💡 Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the Flask application
& ".venv\Scripts\python.exe" app.py
