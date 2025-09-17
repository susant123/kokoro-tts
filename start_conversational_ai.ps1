# Kokoro AI Conversational System (PowerShell)

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "   🤖 Kokoro AI Conversational System" -ForegroundColor Yellow
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (!(Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run the setup first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "🔧 Starting Kokoro AI Conversational System..." -ForegroundColor Green
Write-Host ""
Write-Host "Available interfaces:" -ForegroundColor Cyan
Write-Host "  🌐 Web Interface: http://localhost:5002" -ForegroundColor White
Write-Host "  💬 CLI Chat: Run 'python conversational_ai.py'" -ForegroundColor White
Write-Host ""
Write-Host "💡 Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the web interface
& ".venv\Scripts\python.exe" conversational_web.py