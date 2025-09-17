# 🚀 How To Run Kokoro TTS

A comprehensive guide to running all components of the Kokoro TTS system.

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [CLI Text-to-Speech](#cli-text-to-speech)
- [Web Interface](#web-interface)
- [Conversation Generator](#conversation-generator)
- [Voice Samples](#voice-samples)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)

---

## 🎯 Quick Start

### Prerequisites

- ✅ Python 3.12+ installed
- ✅ Virtual environment set up (`.venv` or `.venv312`)
- ✅ Dependencies installed (`pip install -r requirements.txt`)
- ✅ Model files downloaded (`kokoro-v1.0.onnx`, `voices-v1.0.bin`)

### Quick Test

```powershell
# Windows PowerShell
.\kokoro.ps1 sample.txt test_output.wav --voice af_sarah

# Or activate environment manually
.\.venv\Scripts\Activate.ps1
python kokoro-tts sample.txt test_output.wav --voice af_sarah
```

---

## 🎤 CLI Text-to-Speech

### Basic Commands

#### Using PowerShell Launcher (Recommended)

```powershell
# Convert text file to audio
.\kokoro.ps1 input.txt output.wav --voice af_sarah

# Stream audio (no file output)
.\kokoro.ps1 input.txt --stream --voice af_sarah

# Convert with specific speed
.\kokoro.ps1 input.txt output.wav --voice af_sarah --speed 1.2
```

#### Using Batch File (Windows)

```cmd
kokoro.bat input.txt output.wav --voice af_sarah
```

#### Direct Python Execution

```powershell
# Activate virtual environment first
.\.venv\Scripts\Activate.ps1

# Then run Kokoro TTS
python kokoro-tts input.txt output.wav --voice af_sarah
```

### Advanced CLI Options

#### Voice Management

```powershell
# List all available voices
.\kokoro.ps1 --list-voices

# Use different voice categories
.\kokoro.ps1 input.txt output.wav --voice af_bella    # US Female
.\kokoro.ps1 input.txt output.wav --voice am_adam     # US Male
.\kokoro.ps1 input.txt output.wav --voice bf_emma     # British Female
```

#### Input Formats

```powershell
# Text file
.\kokoro.ps1 document.txt output.wav

# PDF file
.\kokoro.ps1 document.pdf output.wav

# EPUB book
.\kokoro.ps1 book.epub output.wav

# Direct text input
echo "Hello world" | .\kokoro.ps1 - output.wav

# Standard input
.\kokoro.ps1 - output.wav  # Then type your text
```

#### Output Options

```powershell
# WAV output (default)
.\kokoro.ps1 input.txt output.wav

# MP3 output
.\kokoro.ps1 input.txt output.mp3

# Streaming (no file)
.\kokoro.ps1 input.txt --stream

# Custom speed
.\kokoro.ps1 input.txt output.wav --speed 0.8  # Slower
.\kokoro.ps1 input.txt output.wav --speed 1.5  # Faster
```

---

## 🌐 Web Interface

### Starting the Web Server

#### Option 1: PowerShell Launcher

```powershell
.\start_web.ps1
```

#### Option 2: Batch File

```cmd
start_web.bat
```

#### Option 3: Direct Python

```powershell
.\.venv\Scripts\Activate.ps1
python app.py
```

### Accessing the Web Interface

- **URL**: http://localhost:5000
- **Features**:
  - Text-to-speech conversion
  - Voice selection dropdown
  - Voice samples with preview
  - Real-time audio generation
  - Download generated audio

### Web Interface Features

✅ **Text Input**: Type or paste text directly  
✅ **Voice Selection**: Choose from 27+ English voices  
✅ **Voice Samples**: Preview all voices with sample text  
✅ **Speed Control**: Adjust speech speed (0.5x - 2.0x)  
✅ **Audio Download**: Save generated speech as WAV files  
✅ **Responsive Design**: Works on desktop and mobile

---

## 💬 Conversation Generator

### Starting the Conversation Generator

#### Option 1: Direct Python

```powershell
.\.venv\Scripts\Activate.ps1
python conversation_app.py
```

#### Option 2: Manual Activation

```powershell
# Activate environment
.\.venv\Scripts\Activate.ps1

# Run conversation generator
python conversation_app.py
```

### Accessing the Conversation Generator

- **URL**: http://localhost:5001
- **Features**:
  - Multi-voice conversations
  - Voice preview for each message
  - Sample voices tab
  - Conversation settings
  - Audio generation and download

### Using the Conversation Generator

#### Tab 1: Conversation Generator

1. **Add Messages**: Click "Add Message" to create conversation parts
2. **Select Voices**: Choose different voices for each message
3. **Voice Preview**: Automatic preview when voice is selected
4. **Add Text**: Type what each voice should say
5. **Adjust Settings**:
   - Speech speed (0.5x - 2.0x)
   - Pause between messages (0.1s - 2.0s)
6. **Generate**: Click "Generate Conversation"
7. **Download**: Save the complete conversation

#### Tab 2: Sample Voices

1. **Browse Voices**: Listen to all 27 English voices
2. **Preview Audio**: Click play on any voice sample
3. **Add to Conversation**: Click button to add voice to conversation
4. **Auto-Switch**: Automatically switches to conversation tab

---

## 🎵 Voice Samples

### Generating Voice Samples

```powershell
.\.venv\Scripts\Activate.ps1
python generate_voice_samples.py
```

### Sample Text Used

```
"Welcome to WinSera. We provide free Text To Speech service. This project is based on Kokoro TTS."
```

### Available Voice Categories

- **US Female Voices** (11 voices): af_sarah, af_bella, af_nicole, etc.
- **US Male Voices** (8 voices): am_adam, am_michael, etc.
- **British Voices** (8 voices): bf_emma, bf_isabella, bm_george, etc.

### Generated Files Location

```
static/voice_samples/
├── index.json          # Voice samples metadata
├── af_sarah.wav        # Individual voice samples
├── af_bella.wav
├── ...
└── bm_william.wav
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Virtual Environment Not Found

```
❌ Virtual environment not found!
```

**Solution:**

```powershell
# Create virtual environment
python -m venv .venv

# Activate it
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

#### 2. Module Not Found Errors

```
ModuleNotFoundError: No module named 'flask'
```

**Solution:**

```powershell
# Ensure virtual environment is active
.\.venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

#### 3. Model Files Missing

```
FileNotFoundError: [Errno 2] No such file or directory: 'kokoro-v1.0.onnx'
```

**Solution:**

- Ensure `kokoro-v1.0.onnx` and `voices-v1.0.bin` are in the project root
- Check file sizes: ONNX ~310MB, voices ~27MB

#### 4. Port Already in Use

```
OSError: [Errno 10048] Only one usage of each socket address
```

**Solution:**

```powershell
# Find process using the port
netstat -ano | findstr :5000

# Kill the process (replace PID)
taskkill /PID <process_id> /F

# Or use different ports
python app.py --port 5002
```

#### 5. Voice Samples Not Loading

```
Voice samples not available
```

**Solution:**

```powershell
# Generate voice samples
.\.venv\Scripts\Activate.ps1
python generate_voice_samples.py

# Verify samples directory
ls static/voice_samples/
```

### Performance Issues

#### Slow Audio Generation

- **GPU Support**: Install ONNX Runtime GPU if you have NVIDIA GPU
- **Memory**: Ensure at least 4GB RAM available
- **Storage**: Check available disk space for temp files

#### Web Interface Slow

- **Browser Cache**: Clear browser cache and cookies
- **Network**: Check localhost connection
- **Antivirus**: Add project folder to antivirus exclusions

---

## ⚡ Advanced Usage

### Running Multiple Instances

```powershell
# Main TTS web interface (port 5000)
python app.py

# Conversation generator (port 5001) - in new terminal
python conversation_app.py

# Custom port for additional instance
python app.py --port 5002
```

### Batch Processing

```powershell
# Process multiple files
foreach ($file in Get-ChildItem *.txt) {
    .\kokoro.ps1 $file.Name "$($file.BaseName).wav" --voice af_sarah
}

# Different voices for different files
.\kokoro.ps1 chapter1.txt chapter1.wav --voice af_sarah
.\kokoro.ps1 chapter2.txt chapter2.wav --voice af_bella
.\kokoro.ps1 chapter3.txt chapter3.wav --voice am_adam
```

### Voice Blending (Advanced)

```powershell
# Blend multiple voices with weights
.\kokoro.ps1 input.txt output.wav --voice af_sarah:0.7,af_bella:0.3
```

### Development Mode

```powershell
# Run with debug output
python app.py --debug

# Run conversation generator with debug
python conversation_app.py --debug
```

---

## 📊 Quick Reference

### Common Commands

| Purpose          | Command                                              |
| ---------------- | ---------------------------------------------------- |
| Basic TTS        | `.\kokoro.ps1 input.txt output.wav --voice af_sarah` |
| Web Interface    | `.\start_web.ps1` → http://localhost:5000            |
| Conversations    | `python conversation_app.py` → http://localhost:5001 |
| List Voices      | `.\kokoro.ps1 --list-voices`                         |
| Generate Samples | `python generate_voice_samples.py`                   |
| Stream Audio     | `.\kokoro.ps1 input.txt --stream --voice af_sarah`   |

### File Extensions Supported

- **Text**: `.txt`, `.md`
- **Documents**: `.pdf`, `.epub`
- **Output**: `.wav`, `.mp3`

### Default Ports

- **Main Web Interface**: 5000
- **Conversation Generator**: 5001

---

_For more detailed information, check the other documentation files: `README.md`, `SETUP_GUIDE.md`, `WEB_FRONTEND.md`_
