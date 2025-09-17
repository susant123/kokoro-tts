#!/usr/bin/env python3
"""
Simple test script for Kokoro TTS installation
"""

import sys
import os

def test_installation():
    print("🔍 Testing Kokoro TTS Installation...")
    print("=" * 50)
    
    # Check Python version
    python_version = sys.version_info
    print(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check if model files exist
    model_file = "kokoro-v1.0.onnx"
    voices_file = "voices-v1.0.bin"
    
    if os.path.exists(model_file):
        size_mb = os.path.getsize(model_file) / (1024 * 1024)
        print(f"✅ Model file found: {model_file} ({size_mb:.1f} MB)")
    else:
        print(f"❌ Model file missing: {model_file}")
    
    if os.path.exists(voices_file):
        size_mb = os.path.getsize(voices_file) / (1024 * 1024)
        print(f"✅ Voices file found: {voices_file} ({size_mb:.1f} MB)")
    else:
        print(f"❌ Voices file missing: {voices_file}")
    
    # Check required packages
    required_packages = [
        'numpy', 'onnxruntime', 'kokoro_onnx', 'sounddevice', 
        'soundfile', 'bs4', 'ebooklib'
    ]
    
    print("\n📦 Checking Python packages:")
    for package in required_packages:
        try:
            module = __import__(package)
            if package == 'kokoro_onnx':
                # Try to get version, fallback to "installed" if no version attribute
                try:
                    version = getattr(module, '__version__', 'installed')
                    print(f"✅ {package}: {version}")
                except:
                    print(f"✅ {package}: installed")
            else:
                print(f"✅ {package}: installed")
        except ImportError:
            print(f"❌ {package}: not installed")
    
    print("\n🎯 Installation test completed!")
    print("\nNext steps:")
    print("1. Test with: python kokoro-tts sample.txt --stream --voice af_sarah")
    print("2. If model errors occur, try downloading from alternative sources")
    print("3. Check SETUP_GUIDE.md for detailed usage instructions")

if __name__ == "__main__":
    test_installation()
