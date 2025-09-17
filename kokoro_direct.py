#!/usr/bin/env python3
"""
Direct Kokoro TTS wrapper using the kokoro_onnx library
This bypasses the CLI script and uses the library directly
"""

import sys
import os
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Kokoro TTS Direct')
    parser.add_argument('input_file', help='Input text file')
    parser.add_argument('output_file', nargs='?', help='Output audio file')
    parser.add_argument('--voice', default='af_sarah', help='Voice to use')
    parser.add_argument('--speed', type=float, default=1.0, help='Speech speed')
    parser.add_argument('--lang', default='en-us', help='Language')
    parser.add_argument('--format', default='wav', help='Audio format')
    parser.add_argument('--stream', action='store_true', help='Stream audio')
    
    args = parser.parse_args()
    
    # Read input text
    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            text = f.read().strip()
    except Exception as e:
        print(f"Error reading input file: {e}")
        return 1
    
    if not text:
        print("Error: Input text is empty")
        return 1
    
    # Try to import and use kokoro_onnx directly
    try:
        print("Loading Kokoro TTS...")
        from kokoro_onnx import Kokoro
        
        # Initialize with correct model path
        model_path = "kokoro-v1.0.onnx"
        voices_path = "voices-v1.0.bin"
        
        if not os.path.exists(model_path):
            print(f"Error: Model file not found: {model_path}")
            return 1
            
        if not os.path.exists(voices_path):
            print(f"Error: Voices file not found: {voices_path}")
            return 1
        
        # Create TTS instance
        tts = Kokoro(model_path, voices_path)
        
        print(f"Generating audio with voice: {args.voice}")
        
        # Generate audio
        audio_data = tts.generate(text, voice=args.voice, speed=args.speed)
        
        if args.stream:
            # Stream audio using sounddevice
            try:
                import sounddevice as sd
                import numpy as np
                
                # Assume audio_data is float32 array
                if isinstance(audio_data, list):
                    audio_data = np.array(audio_data, dtype=np.float32)
                
                print("Playing audio...")
                sd.play(audio_data, samplerate=24000)  # Kokoro uses 24kHz
                sd.wait()
                print("Audio playback completed.")
                
            except ImportError:
                print("Error: sounddevice not available for streaming")
                return 1
        else:
            # Save to file
            if not args.output_file:
                args.output_file = "output.wav"
                
            try:
                import soundfile as sf
                
                # Save audio
                sf.write(args.output_file, audio_data, samplerate=24000)
                print(f"Audio saved to: {args.output_file}")
                
            except ImportError:
                print("Error: soundfile not available for saving")
                return 1
        
        return 0
        
    except ImportError as e:
        print(f"Error importing kokoro_onnx: {e}")
        print("Falling back to original CLI method...")
        
        # Fallback to original method
        return run_original_cli(args)
        
    except Exception as e:
        print(f"Error with direct kokoro_onnx: {e}")
        print("Falling back to original CLI method...")
        
        return run_original_cli(args)

def run_original_cli(args):
    """Fallback to the original CLI script"""
    import subprocess
    
    cmd = [
        sys.executable,
        "kokoro-tts",
        args.input_file
    ]
    
    if not args.stream and args.output_file:
        cmd.append(args.output_file)
    
    cmd.extend([
        "--voice", args.voice,
        "--speed", str(args.speed),
        "--lang", args.lang,
        "--format", args.format
    ])
    
    if args.stream:
        cmd.append("--stream")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Audio generated successfully!")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"Error: {result.stderr}")
            
        return result.returncode
        
    except Exception as e:
        print(f"Error running CLI: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
