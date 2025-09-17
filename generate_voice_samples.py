#!/usr/bin/env python3
"""
Voice Samples Generator for Kokoro TTS
Generates sample audio files for all English voices
"""

import os
import sys
import subprocess
from pathlib import Path

# Configuration
PYTHON_EXE = r"D:\00\kokoro\.venv312\Scripts\python.exe"
KOKORO_SCRIPT = "kokoro-tts"
SAMPLE_TEXT = "Welcome to WinSera. We provide free Text To Speech service. This project is based on Kokoro TTS."
SAMPLES_DIR = os.path.join("static", "voice_samples")

# English voices from app.py
ENGLISH_VOICES = {
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
    }
}

def ensure_samples_directory():
    """Create samples directory if it doesn't exist"""
    os.makedirs(SAMPLES_DIR, exist_ok=True)
    print(f"✅ Samples directory: {SAMPLES_DIR}")

def generate_voice_sample(voice_id, voice_name, category):
    """Generate a single voice sample"""
    output_file = os.path.join(SAMPLES_DIR, f"{voice_id}.wav")
    
    # Skip if file already exists
    if os.path.exists(output_file):
        print(f"⏭️  Skipping {voice_name} ({voice_id}) - already exists")
        return True
    
    # Create temporary input file
    temp_input = f"temp_sample_{voice_id}.txt"
    try:
        with open(temp_input, 'w', encoding='utf-8') as f:
            f.write(SAMPLE_TEXT)
        
        # Determine language based on category
        language = "en-gb" if "GB" in category else "en-us"
        
        # Generate command
        cmd = [
            PYTHON_EXE,
            KOKORO_SCRIPT,
            temp_input,
            output_file,
            "--voice", voice_id,
            "--speed", "1.0",
            "--lang", language,
            "--format", "wav"
        ]
        
        print(f"🎤 Generating {voice_name} ({voice_id})...")
        
        # Run the command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=os.getcwd()
        )
        
        if result.returncode == 0 and os.path.exists(output_file):
            print(f"✅ Successfully generated {voice_name}")
            return True
        else:
            print(f"❌ Failed to generate {voice_name}: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error generating {voice_name}: {e}")
        return False
    finally:
        # Clean up temporary file
        if os.path.exists(temp_input):
            try:
                os.remove(temp_input)
            except:
                pass

def generate_all_samples():
    """Generate samples for all English voices"""
    print("🎭 Kokoro TTS Voice Samples Generator")
    print("=" * 50)
    print(f"Sample Text: '{SAMPLE_TEXT}'")
    print("=" * 50)
    
    ensure_samples_directory()
    
    total_voices = 0
    successful = 0
    failed = 0
    
    for category, voices in ENGLISH_VOICES.items():
        print(f"\n📂 {category}")
        print("-" * 30)
        
        for voice_id, voice_name in voices.items():
            total_voices += 1
            if generate_voice_sample(voice_id, voice_name, category):
                successful += 1
            else:
                failed += 1
    
    print("\n" + "=" * 50)
    print("🎉 Generation Complete!")
    print(f"📊 Total Voices: {total_voices}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📁 Samples saved to: {SAMPLES_DIR}")
    
    return successful, failed

def create_samples_index():
    """Create an index file listing all samples"""
    index_file = os.path.join(SAMPLES_DIR, "index.json")
    
    samples_data = {
        "generated_at": "2025-08-13",
        "sample_text": SAMPLE_TEXT,
        "categories": {}
    }
    
    for category, voices in ENGLISH_VOICES.items():
        samples_data["categories"][category] = {}
        for voice_id, voice_name in voices.items():
            sample_file = f"{voice_id}.wav"
            sample_path = os.path.join(SAMPLES_DIR, sample_file)
            
            if os.path.exists(sample_path):
                file_size = os.path.getsize(sample_path)
                samples_data["categories"][category][voice_id] = {
                    "name": voice_name,
                    "file": sample_file,
                    "url": f"/static/voice_samples/{sample_file}",
                    "size_bytes": file_size,
                    "size_kb": round(file_size / 1024, 1)
                }
    
    import json
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(samples_data, f, indent=2, ensure_ascii=False)
    
    print(f"📋 Created samples index: {index_file}")

if __name__ == "__main__":
    try:
        successful, failed = generate_all_samples()
        create_samples_index()
        
        if failed == 0:
            print("\n🎊 All voice samples generated successfully!")
            print("Ready to add to the web interface!")
        else:
            print(f"\n⚠️  {failed} samples failed to generate. Check the errors above.")
            
    except KeyboardInterrupt:
        print("\n⏹️  Generation stopped by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
