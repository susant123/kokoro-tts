#!/usr/bin/env python3
"""
Kokoro TTS Python Version Checker and Fixer
This script helps resolve Python 3.13 compatibility issues
"""

import sys
import subprocess
import os
from pathlib import Path

def check_python_versions():
    """Check available Python versions"""
    print("🐍 Checking available Python versions...")
    print("=" * 50)
    
    try:
        result = subprocess.run(["py", "-0"], capture_output=True, text=True)
        if result.returncode == 0:
            print("Available Python versions:")
            print(result.stdout)
            
            # Check if Python 3.12 is available
            if "3.12" in result.stdout:
                print("✅ Python 3.12 is available!")
                return True
            else:
                print("❌ Python 3.12 is NOT available")
                return False
        else:
            print("Could not check Python versions with 'py' launcher")
            return False
    except FileNotFoundError:
        print("Python launcher 'py' not found")
        return False

def create_python312_env():
    """Create a Python 3.12 virtual environment"""
    print("\n🔧 Creating Python 3.12 virtual environment...")
    
    try:
        # Create new venv with Python 3.12
        cmd = ["py", "-3.12", "-m", "venv", ".venv312"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Python 3.12 virtual environment created!")
            
            # Install requirements
            print("📦 Installing requirements...")
            pip_cmd = [".venv312\\Scripts\\python.exe", "-m", "pip", "install", "-r", "requirements.txt"]
            pip_result = subprocess.run(pip_cmd, capture_output=True, text=True)
            
            if pip_result.returncode == 0:
                print("✅ Requirements installed successfully!")
                return True
            else:
                print(f"❌ Failed to install requirements: {pip_result.stderr}")
                return False
        else:
            print(f"❌ Failed to create Python 3.12 environment: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating Python 3.12 environment: {e}")
        return False

def download_install_python312():
    """Provide instructions to download Python 3.12"""
    print("\n📥 Python 3.12 Installation Instructions:")
    print("=" * 50)
    print("1. Go to: https://www.python.org/downloads/release/python-3127/")
    print("2. Download: 'Windows installer (64-bit)' for Python 3.12.7")
    print("3. Run the installer with these options:")
    print("   ✅ Add Python to PATH")
    print("   ✅ Install for all users (optional)")
    print("4. After installation, restart your terminal")
    print("5. Run this script again")
    print("\nAlternatively, you can use winget:")
    print("   winget install Python.Python.3.12")

def create_workaround_script():
    """Create a workaround script for the current setup"""
    print("\n🛠️ Creating workaround for current setup...")
    
    script_content = '''@echo off
echo.
echo ===============================================
echo   ⚠️  Kokoro TTS Python 3.13 Compatibility Fix
echo ===============================================
echo.
echo This script helps run Kokoro TTS with Python 3.13
echo Note: Some features may not work due to compatibility issues
echo.

REM Check if Python 3.12 environment exists
if exist ".venv312\\Scripts\\python.exe" (
    echo ✅ Using Python 3.12 environment
    set PYTHON_EXE=.venv312\\Scripts\\python.exe
) else (
    echo ⚠️  Using Python 3.13 environment (compatibility issues expected)
    set PYTHON_EXE=.venv\\Scripts\\python.exe
)

REM Run with the appropriate Python version
echo Starting Kokoro TTS Web Frontend...
"%PYTHON_EXE%" app.py

pause
'''
    
    try:
        with open("start_web_fixed.bat", "w") as f:
            f.write(script_content)
        print("✅ Created 'start_web_fixed.bat' - use this to start the web frontend")
        
        # Also create PowerShell version
        ps_content = '''# Kokoro TTS Python 3.13 Compatibility Fix

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "  ⚠️  Kokoro TTS Python 3.13 Compatibility Fix" -ForegroundColor Yellow  
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python 3.12 environment exists
if (Test-Path ".venv312\\Scripts\\python.exe") {
    Write-Host "✅ Using Python 3.12 environment" -ForegroundColor Green
    $pythonExe = ".venv312\\Scripts\\python.exe"
} else {
    Write-Host "⚠️  Using Python 3.13 environment (compatibility issues expected)" -ForegroundColor Yellow
    $pythonExe = ".venv\\Scripts\\python.exe"
}

Write-Host "Starting Kokoro TTS Web Frontend..." -ForegroundColor Cyan
& $pythonExe app.py
'''
        
        with open("start_web_fixed.ps1", "w") as f:
            f.write(ps_content)
        print("✅ Created 'start_web_fixed.ps1' - PowerShell version")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create workaround script: {e}")
        return False

def show_current_status():
    """Show current Python environment status"""
    print("\n📊 Current Status:")
    print("=" * 30)
    print(f"Current Python: {sys.version}")
    print(f"Current executable: {sys.executable}")
    
    # Check if model files exist
    model_exists = os.path.exists("kokoro-v1.0.onnx")
    voices_exists = os.path.exists("voices-v1.0.bin")
    
    print(f"Model file: {'✅' if model_exists else '❌'}")
    print(f"Voices file: {'✅' if voices_exists else '❌'}")
    
    # Check environments
    venv_exists = os.path.exists(".venv/Scripts/python.exe")
    venv312_exists = os.path.exists(".venv312/Scripts/python.exe")
    
    print(f"Python 3.13 env: {'✅' if venv_exists else '❌'}")
    print(f"Python 3.12 env: {'✅' if venv312_exists else '❌'}")

def main():
    print("🔍 Kokoro TTS Python Compatibility Checker")
    print("=" * 50)
    
    show_current_status()
    
    # Check if Python 3.12 is available
    has_python312 = check_python_versions()
    
    if has_python312:
        print("\n🎯 Recommended solution: Create Python 3.12 environment")
        response = input("Would you like to create a Python 3.12 environment? (y/n): ").lower().strip()
        
        if response == 'y':
            if create_python312_env():
                print("\n🎉 Success! Use the Python 3.12 environment:")
                print("   start_web_fixed.bat  (or start_web_fixed.ps1)")
            else:
                print("\n⚠️ Creating workaround for current setup...")
                create_workaround_script()
        else:
            print("\n⚠️ Creating workaround for current setup...")
            create_workaround_script()
    else:
        print("\n❌ Python 3.12 not found on system")
        download_install_python312()
        print("\n⚠️ Creating workaround for current setup...")
        create_workaround_script()
    
    print("\n🎯 Next Steps:")
    print("1. If you installed Python 3.12: Use 'start_web_fixed.bat'")
    print("2. If staying with Python 3.13: Expect some compatibility issues")
    print("3. For best results: Install Python 3.12 and recreate environment")

if __name__ == "__main__":
    main()
