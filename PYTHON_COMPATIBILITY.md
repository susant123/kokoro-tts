# 🐍 Kokoro TTS Python Compatibility Issues & Solutions

## 🚨 **The Problem**

Kokoro TTS is experiencing compatibility issues because:

- **Current Setup**: Python 3.13.5
- **Required Version**: Python 3.12.x
- **Error**: `INVALID_PROTOBUF` / `Protobuf parsing failed`

The ONNX model file is **NOT corrupted** - it's a Python version compatibility issue.

## ✅ **Solutions (In Order of Preference)**

### **Solution 1: Install Python 3.12 (RECOMMENDED)**

#### Step 1: Install Python 3.12

```cmd
# Option A: Using winget (if available)
winget install Python.Python.3.12

# Option B: Manual download
# Go to: https://www.python.org/downloads/release/python-3127/
# Download: Windows installer (64-bit)
# Install with "Add to PATH" checked
```

#### Step 2: Create Python 3.12 Environment

```cmd
# Navigate to kokoro folder
cd D:\00\kokoro

# Create new environment with Python 3.12
py -3.12 -m venv .venv312

# Activate the new environment
.venv312\Scripts\activate

# Install requirements
python -m pip install -r requirements.txt

# Download model files (if needed)
# They should already be present
```

#### Step 3: Use Python 3.12 Environment

```cmd
# Start web frontend with Python 3.12
.venv312\Scripts\python.exe app.py

# Or use the fixed launcher
start_web_fixed.bat
```

### **Solution 2: Workaround with Python 3.13**

If you can't install Python 3.12, you can try these workarounds:

#### Option A: Use Fixed Launcher

```cmd
# Use the compatibility-aware launcher
start_web_fixed.bat
```

#### Option B: Try Alternative TTS Libraries

You could try using other TTS libraries that are Python 3.13 compatible:

- `pyttsx3`
- `gTTS` (Google Text-to-Speech)
- `azure-cognitiveservices-speech`

### **Solution 3: Docker Alternative (Advanced)**

Create a Docker container with Python 3.12:

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app.py"]
```

## 🔧 **Quick Fix Commands**

### Check Python Versions Available

```cmd
py -0
```

### Install Python 3.12 (if not present)

```cmd
winget install Python.Python.3.12
```

### Create Python 3.12 Environment

```cmd
py -3.12 -m venv .venv312
.venv312\Scripts\python -m pip install -r requirements.txt
```

### Test with Python 3.12

```cmd
.venv312\Scripts\python.exe kokoro-tts sample.txt --stream --voice af_sarah
```

## 📊 **Compatibility Matrix**

| Python Version | Kokoro TTS | ONNX Runtime | Status               |
| -------------- | ---------- | ------------ | -------------------- |
| 3.9.x          | ✅ Works   | ✅ Works     | ✅ Supported         |
| 3.10.x         | ✅ Works   | ✅ Works     | ✅ Supported         |
| 3.11.x         | ✅ Works   | ✅ Works     | ✅ Supported         |
| 3.12.x         | ✅ Works   | ✅ Works     | ✅ **RECOMMENDED**   |
| 3.13.x         | ❌ Issues  | ⚠️ Limited   | ❌ **NOT SUPPORTED** |

## 🎯 **Verification Steps**

After installing Python 3.12:

1. **Check Installation**:

   ```cmd
   py -3.12 --version
   ```

2. **Test TTS CLI**:

   ```cmd
   .venv312\Scripts\python.exe kokoro-tts sample.txt --stream
   ```

3. **Test Web Frontend**:
   ```cmd
   .venv312\Scripts\python.exe app.py
   # Visit: http://localhost:5000
   ```

## 🚨 **Important Notes**

- **Don't delete the current .venv folder** - keep it as backup
- **The model files are fine** - no need to re-download
- **Python 3.13 support may come later** - this is a temporary limitation
- **Web frontend will work** once Python compatibility is resolved

## 🆘 **If Nothing Works**

As a last resort, you can use alternative TTS options:

### Option 1: Simple TTS with pyttsx3

```python
import pyttsx3

engine = pyttsx3.init()
engine.say("Hello, this is a test")
engine.runAndWait()
```

### Option 2: Google TTS (requires internet)

```python
from gtts import gTTS
import pygame

tts = gTTS("Hello world", lang='en')
tts.save("output.mp3")
```

## 📞 **Getting Help**

1. **Check Python version**: `py -0`
2. **Run compatibility checker**: `python fix_python_version.py`
3. **Test with Python 3.12**: Install it first, then test
4. **Check project documentation**: `README.md` and `SETUP_GUIDE.md`

---

**Summary**: The issue is **NOT** with the downloaded files - it's a Python 3.13 compatibility problem. Install Python 3.12 for the best experience! 🐍✅
