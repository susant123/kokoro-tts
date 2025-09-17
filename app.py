"""
Kokoro TTS Web Frontend
A Flask-based web interface for the Kokoro TTS system
Optimized for GPU acceleration and model preloading
"""

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
import subprocess
import os
import tempfile
import uuid
import json
from datetime import datetime
import threading
import time
from kokoro_onnx import Kokoro

app = Flask(__name__)
app.secret_key = 'kokoro-tts-secret-key-2025'

# Configuration
PYTHON_EXE = os.path.join(os.getcwd(), ".venv", "Scripts", "python.exe")  # Use current environment
KOKORO_SCRIPT = "kokoro-tts"
TEMP_DIR = os.path.join(os.getcwd(), "temp_audio")
MAX_TEXT_LENGTH = 10000

# Global model instance for preloading
kokoro_model = None
model_lock = threading.Lock()

# Enable GPU acceleration
os.environ["ONNX_PROVIDER"] = "CUDAExecutionProvider"

# Ensure temp directory exists
os.makedirs(TEMP_DIR, exist_ok=True)

# Available voices (hardcoded for now, can be fetched dynamically)
VOICES = {
    "English (US) - Female": {
        "af_alloy": "Alloy",
        "af_aoede": "Aoede", 
        "af_bella": "Bella",
        "af_heart": "Heart",
        "af_jessica": "Jessica",
        "af_kore": "Kore",
        "af_nicole": "Nicole",
        "af_nova": "Nova",
        "af_river": "River",
        "af_sarah": "Sarah",
        "af_sky": "Sky"
    },
    "English (US) - Male": {
        "am_adam": "Adam",
        "am_echo": "Echo",
        "am_eric": "Eric",
        "am_fenrir": "Fenrir",
        "am_liam": "Liam",
        "am_michael": "Michael",
        "am_onyx": "Onyx",
        "am_puck": "Puck"
    },
    "English (GB)": {
        "bf_alice": "Alice (F)",
        "bf_emma": "Emma (F)",
        "bf_isabella": "Isabella (F)",
        "bf_lily": "Lily (F)",
        "bm_daniel": "Daniel (M)",
        "bm_fable": "Fable (M)",
        "bm_george": "George (M)",
        "bm_lewis": "Lewis (M)"
    },
    "Other Languages": {
        "ff_siwis": "French - Siwis (F)",
        "if_sara": "Italian - Sara (F)",
        "im_nicola": "Italian - Nicola (M)",
        "jf_alpha": "Japanese - Alpha (F)",
        "jf_gongitsune": "Japanese - Gongitsune (F)",
        "jm_kumo": "Japanese - Kumo (M)",
        "zf_xiaobei": "Chinese - Xiaobei (F)",
        "zm_yunjian": "Chinese - Yunjian (M)"
    }
}

LANGUAGES = {
    "en-us": "English (US)",
    "en-gb": "English (GB)", 
    "fr-fr": "French",
    "it": "Italian",
    "ja": "Japanese",
    "cmn": "Chinese (Mandarin)"
}

def get_kokoro_model():
    """Get or initialize the global Kokoro model instance"""
    global kokoro_model
    
    with model_lock:
        if kokoro_model is None:
            try:
                print("🔄 Loading Kokoro model with GPU acceleration...")
                kokoro_model = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")
                print("✅ Model loaded successfully!")
            except Exception as e:
                print(f"❌ Failed to load model: {e}")
                raise
        
        return kokoro_model

def run_tts_command_direct(text, voice="af_sarah", speed=1.0, language="en-us", output_format="wav"):
    """Run TTS using direct model API for better performance"""
    
    # Create temporary audio file
    temp_id = str(uuid.uuid4())
    temp_audio_file = os.path.join(TEMP_DIR, f"output_{temp_id}.{output_format}")
    
    try:
        # Get the preloaded model
        model = get_kokoro_model()
        
        # Generate audio using direct API
        audio_data = model.create(text, voice=voice, speed=speed, lang=language)
        
        # Save audio file
        import soundfile as sf
        if output_format == "wav":
            sf.write(temp_audio_file, audio_data, 24000, format="WAV")
        else:  # mp3
            # For MP3, we still need to use the CLI as it handles format conversion
            return run_tts_command_cli(text, voice, speed, language, output_format)
        
        if os.path.exists(temp_audio_file):
            return {
                "success": True,
                "audio_file": temp_audio_file,
                "message": "Audio generated successfully with GPU acceleration!"
            }
        else:
            return {
                "success": False,
                "error": "Failed to create audio file",
                "message": "Audio generation failed"
            }
            
    except Exception as e:
        print(f"Direct API failed: {e}, falling back to CLI")
        return run_tts_command_cli(text, voice, speed, language, output_format)

def run_tts_command_cli(text, voice="af_sarah", speed=1.0, language="en-us", output_format="wav"):
    """Run the Kokoro TTS CLI command (fallback method)"""
    
    # Create temporary files
    temp_id = str(uuid.uuid4())
    temp_text_file = os.path.join(TEMP_DIR, f"input_{temp_id}.txt")
    temp_audio_file = os.path.join(TEMP_DIR, f"output_{temp_id}.{output_format}")
    
    try:
        # Write text to temporary file with explicit UTF-8 encoding
        with open(temp_text_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        # Construct command
        cmd = [
            PYTHON_EXE,
            KOKORO_SCRIPT,
            temp_text_file,
            temp_audio_file,
            "--voice", voice,
            "--speed", str(speed),
            "--lang", language,
            "--format", output_format
        ]
        
        # Run the command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,  # 2 minute timeout
            cwd=os.getcwd()
        )
        
        if result.returncode == 0 and os.path.exists(temp_audio_file):
            return {
                "success": True,
                "audio_file": temp_audio_file,
                "message": "Audio generated successfully!"
            }
        else:
            error_msg = result.stderr or result.stdout or "Unknown error occurred"
            
            # Check for specific Python compatibility issues
            if "INVALID_PROTOBUF" in error_msg or "Protobuf parsing failed" in error_msg:
                return {
                    "success": False,
                    "error": error_msg,
                    "message": "⚠️ Python 3.13 Compatibility Issue - Kokoro TTS requires Python 3.12. Please install Python 3.12 and recreate the virtual environment.",
                    "fix_suggestion": "Run: py -3.12 -m venv .venv312 && .venv312\\Scripts\\python -m pip install -r requirements.txt"
                }
            
            return {
                "success": False,
                "error": error_msg,
                "message": "Failed to generate audio"
            }
            
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "TTS generation timed out",
            "message": "The text processing took too long"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "An error occurred during processing"
        }
    finally:
        # Clean up temporary text file
        if os.path.exists(temp_text_file):
            try:
                os.remove(temp_text_file)
            except:
                pass

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html', 
                         voices=VOICES, 
                         languages=LANGUAGES)

@app.route('/generate', methods=['POST'])
def generate_audio():
    """Generate audio from text"""
    try:
        data = request.get_json()
        
        # Validate input
        text = data.get('text', '').strip()
        if not text:
            return jsonify({
                "success": False,
                "message": "Please enter some text to convert"
            })
        
        if len(text) > MAX_TEXT_LENGTH:
            return jsonify({
                "success": False,
                "message": f"Text is too long. Maximum {MAX_TEXT_LENGTH} characters allowed."
            })
        
        voice = data.get('voice', 'af_sarah')
        speed = float(data.get('speed', 1.0))
        language = data.get('language', 'en-us')
        output_format = data.get('format', 'wav')
        
        # Validate parameters
        if speed < 0.5 or speed > 2.0:
            speed = 1.0
            
        # Generate audio
        result = run_tts_command_direct(text, voice, speed, language, output_format)
        
        if result["success"]:
            # Return the file path for download
            return jsonify({
                "success": True,
                "audio_file": os.path.basename(result["audio_file"]),
                "message": result["message"]
            })
        else:
            return jsonify(result)
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        })

@app.route('/download/<filename>')
def download_file(filename):
    """Download generated audio file"""
    try:
        file_path = os.path.join(TEMP_DIR, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return "File not found", 404
    except Exception as e:
        return f"Error downloading file: {str(e)}", 500

@app.route('/cleanup')
def cleanup_temp_files():
    """Clean up old temporary files"""
    try:
        count = 0
        current_time = time.time()
        
        for filename in os.listdir(TEMP_DIR):
            file_path = os.path.join(TEMP_DIR, filename)
            # Delete files older than 1 hour
            if os.path.isfile(file_path) and current_time - os.path.getctime(file_path) > 3600:
                try:
                    os.remove(file_path)
                    count += 1
                except:
                    pass
        
        return jsonify({
            "success": True,
            "message": f"Cleaned up {count} temporary files"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Cleanup error: {str(e)}"
        })

@app.route('/voice_samples')
def get_voice_samples():
    """Get voice samples data"""
    try:
        samples_index_path = os.path.join("static", "voice_samples", "index.json")
        if os.path.exists(samples_index_path):
            with open(samples_index_path, 'r', encoding='utf-8') as f:
                samples_data = json.load(f)
            return jsonify(samples_data)
        else:
            return jsonify({
                "error": "Voice samples not found",
                "message": "Run generate_voice_samples.py to create samples"
            })
    except Exception as e:
        return jsonify({
            "error": "Failed to load voice samples",
            "message": str(e)
        })

@app.route('/status')
def status():
    """Check system status"""
    try:
        # Check if model files exist
        model_exists = os.path.exists("kokoro-v1.0.onnx")
        voices_exist = os.path.exists("voices-v1.0.bin")
        python_exists = os.path.exists(PYTHON_EXE)
        
        # Count temporary files
        temp_files = len([f for f in os.listdir(TEMP_DIR) if os.path.isfile(os.path.join(TEMP_DIR, f))])
        
        return jsonify({
            "model_file": model_exists,
            "voices_file": voices_exist,
            "python_env": python_exists,
            "temp_files": temp_files,
            "status": "ready" if all([model_exists, voices_exist, python_exists]) else "error"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

if __name__ == '__main__':
    print("🎤 Starting Kokoro TTS Web Frontend...")
    print("📡 Server will be available at: http://localhost:5000")
    print("🔧 GPU acceleration enabled")
    
    # Preload the model
    try:
        print("🔄 Preloading Kokoro model...")
        get_kokoro_model()
        print("🚀 Model preloaded! Ready for fast inference.")
    except Exception as e:
        print(f"⚠️  Model preload failed: {e}")
        print("🔄 Will load model on first request.")
    
    # Start cleanup thread
    def cleanup_thread():
        while True:
            time.sleep(3600)  # Run every hour
            try:
                cleanup_temp_files()
            except:
                pass
    
    threading.Thread(target=cleanup_thread, daemon=True).start()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
