"""
Kokoro TTS Conversation Generator
Creates conversations between multiple voices
"""

from flask import Flask, render_template, request, jsonify, send_file
import subprocess
import os
import tempfile
import uuid
import json
from datetime import datetime
import threading
import time
import wave
import numpy as np

app = Flask(__name__)
app.secret_key = 'kokoro-conversation-2025'

# Add tojson filter to Jinja environment
@app.template_filter('tojson')
def tojson_filter(obj):
    import json
    return json.dumps(obj)

# Configuration
PYTHON_EXE = r"D:\00\kokoro\.venv312\Scripts\python.exe"
KOKORO_SCRIPT = "kokoro-tts"
TEMP_DIR = os.path.join(os.getcwd(), "temp_conversations")
MAX_TEXT_LENGTH = 1000  # Per message
MAX_CONVERSATION_LENGTH = 20  # Max number of messages

# Ensure temp directory exists
os.makedirs(TEMP_DIR, exist_ok=True)

# Available voices for conversations
CONVERSATION_VOICES = {
    "English (US) - Female": {
        "af_sarah": "Sarah (Calm, Professional)",
        "af_bella": "Bella (Warm, Friendly)",
        "af_nova": "Nova (Energetic, Young)",
        "af_jessica": "Jessica (Mature, Wise)",
        "af_river": "River (Soft, Gentle)",
        "af_sky": "Sky (Bright, Cheerful)"
    },
    "English (US) - Male": {
        "am_adam": "Adam (Deep, Confident)",
        "am_liam": "Liam (Young, Casual)",
        "am_michael": "Michael (Professional, Clear)",
        "am_eric": "Eric (Friendly, Approachable)",
        "am_echo": "Echo (Mysterious, Dramatic)",
        "am_onyx": "Onyx (Strong, Authoritative)"
    },
    "English (GB)": {
        "bf_alice": "Alice (British, Elegant)",
        "bf_emma": "Emma (British, Warm)",
        "bm_daniel": "Daniel (British, Gentleman)",
        "bm_george": "George (British, Distinguished)"
    }
}

def generate_single_audio(text, voice, speed=1.0, temp_id=""):
    """Generate audio for a single message"""
    temp_text_file = os.path.join(TEMP_DIR, f"msg_{temp_id}_{voice}.txt")
    temp_audio_file = os.path.join(TEMP_DIR, f"msg_{temp_id}_{voice}.wav")
    
    try:
        # Write text to temporary file
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
            "--lang", "en-us",
            "--format", "wav"
        ]
        
        # Run the command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=os.getcwd()
        )
        
        if result.returncode == 0 and os.path.exists(temp_audio_file):
            return temp_audio_file
        else:
            print(f"Error generating audio for voice {voice}: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"Exception generating audio: {e}")
        return None
    finally:
        # Clean up temporary text file
        if os.path.exists(temp_text_file):
            try:
                os.remove(temp_text_file)
            except:
                pass

def combine_audio_files(audio_files, output_file, silence_duration=0.5):
    """Combine multiple WAV files with silence between them"""
    try:
        import soundfile as sf
        
        combined_audio = []
        sample_rate = 24000  # Kokoro TTS sample rate
        silence_samples = int(silence_duration * sample_rate)
        silence = np.zeros(silence_samples, dtype=np.float32)
        
        for i, audio_file in enumerate(audio_files):
            if os.path.exists(audio_file):
                # Read audio file
                audio_data, sr = sf.read(audio_file)
                
                # Ensure it's float32
                if audio_data.dtype != np.float32:
                    audio_data = audio_data.astype(np.float32)
                
                # Add audio to combined
                combined_audio.extend(audio_data)
                
                # Add silence between messages (except after the last one)
                if i < len(audio_files) - 1:
                    combined_audio.extend(silence)
        
        # Convert to numpy array
        combined_audio = np.array(combined_audio, dtype=np.float32)
        
        # Save combined audio
        sf.write(output_file, combined_audio, sample_rate)
        
        # Clean up individual files
        for audio_file in audio_files:
            try:
                if os.path.exists(audio_file):
                    os.remove(audio_file)
            except:
                pass
        
        return True
        
    except Exception as e:
        print(f"Error combining audio files: {e}")
        return False

@app.route('/')
def conversation():
    """Conversation page"""
    import json
    voices_json = json.dumps(CONVERSATION_VOICES)
    return render_template('conversation.html', voices=CONVERSATION_VOICES, voices_json=voices_json)

@app.route('/generate_conversation', methods=['POST'])
def generate_conversation():
    """Generate conversation audio"""
    try:
        data = request.get_json()
        
        # Validate input
        messages = data.get('messages', [])
        if not messages:
            return jsonify({
                "success": False,
                "message": "Please add at least one message to the conversation"
            })
        
        if len(messages) > MAX_CONVERSATION_LENGTH:
            return jsonify({
                "success": False,
                "message": f"Too many messages. Maximum {MAX_CONVERSATION_LENGTH} allowed."
            })
        
        conversation_speed = float(data.get('speed', 1.0))
        silence_duration = float(data.get('silence', 0.5))
        
        # Validate messages
        for i, msg in enumerate(messages):
            text = msg.get('text', '').strip()
            voice = msg.get('voice', '')
            
            if not text:
                return jsonify({
                    "success": False,
                    "message": f"Message {i+1} is empty. Please enter text for all messages."
                })
            
            if len(text) > MAX_TEXT_LENGTH:
                return jsonify({
                    "success": False,
                    "message": f"Message {i+1} is too long. Maximum {MAX_TEXT_LENGTH} characters allowed."
                })
            
            if not voice:
                return jsonify({
                    "success": False,
                    "message": f"Please select a voice for message {i+1}."
                })
        
        # Generate unique ID for this conversation
        conversation_id = str(uuid.uuid4())
        
        # Generate audio for each message
        audio_files = []
        for i, msg in enumerate(messages):
            text = msg['text'].strip()
            voice = msg['voice']
            
            print(f"Generating audio for message {i+1}: {voice}")
            audio_file = generate_single_audio(text, voice, conversation_speed, f"{conversation_id}_{i}")
            
            if audio_file:
                audio_files.append(audio_file)
            else:
                return jsonify({
                    "success": False,
                    "message": f"Failed to generate audio for message {i+1}. Please try again."
                })
        
        # Combine all audio files
        final_audio_file = os.path.join(TEMP_DIR, f"conversation_{conversation_id}.wav")
        
        print(f"Combining {len(audio_files)} audio files...")
        if combine_audio_files(audio_files, final_audio_file, silence_duration):
            return jsonify({
                "success": True,
                "audio_file": os.path.basename(final_audio_file),
                "message": f"Conversation generated successfully! {len(messages)} messages combined.",
                "conversation_info": {
                    "messages": len(messages),
                    "total_characters": sum(len(msg['text']) for msg in messages),
                    "voices_used": list(set(msg['voice'] for msg in messages))
                }
            })
        else:
            return jsonify({
                "success": False,
                "message": "Failed to combine audio files. Please try again."
            })
            
    except Exception as e:
        print(f"Error generating conversation: {e}")
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        })

@app.route('/download_conversation/<filename>')
def download_conversation(filename):
    """Download generated conversation audio"""
    try:
        file_path = os.path.join(TEMP_DIR, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, download_name=f"conversation_{filename}")
        else:
            return "File not found", 404
    except Exception as e:
        return f"Error downloading file: {str(e)}", 500

@app.route('/voice_samples')
def get_voice_samples():
    """Get voice samples data for conversation generator"""
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

@app.route('/cleanup_conversations')
def cleanup_conversations():
    """Clean up old conversation files"""
    try:
        count = 0
        current_time = time.time()
        
        for filename in os.listdir(TEMP_DIR):
            file_path = os.path.join(TEMP_DIR, filename)
            # Delete files older than 2 hours
            if os.path.isfile(file_path) and current_time - os.path.getctime(file_path) > 7200:
                try:
                    os.remove(file_path)
                    count += 1
                except:
                    pass
        
        return jsonify({
            "success": True,
            "message": f"Cleaned up {count} old conversation files"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Cleanup error: {str(e)}"
        })

if __name__ == '__main__':
    print("🎭 Starting Kokoro TTS Conversation Generator...")
    print("📡 Server will be available at: http://localhost:5001")
    print("💬 Create conversations with multiple voices!")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
