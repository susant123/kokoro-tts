#!/usr/bin/env python3
"""
Quick demo script to test the Kokoro TTS Web Frontend
"""

import requests
import json
import time

def test_web_frontend():
    """Test the web frontend API"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Kokoro TTS Web Frontend...")
    print("=" * 50)
    
    # Test 1: Check status
    print("1. Testing system status...")
    try:
        response = requests.get(f"{base_url}/status", timeout=10)
        if response.status_code == 200:
            status_data = response.json()
            print(f"   ✅ Status: {status_data.get('status', 'unknown')}")
            print(f"   📁 Model file: {'✅' if status_data.get('model_file') else '❌'}")
            print(f"   🎭 Voices file: {'✅' if status_data.get('voices_file') else '❌'}")
            print(f"   🐍 Python env: {'✅' if status_data.get('python_env') else '❌'}")
        else:
            print(f"   ❌ Status check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Status check error: {e}")
    
    print()
    
    # Test 2: Generate sample audio
    print("2. Testing audio generation...")
    test_data = {
        "text": "Hello! This is a test of the Kokoro TTS web frontend. The system is working correctly.",
        "voice": "af_sarah",
        "speed": 1.0,
        "language": "en-us",
        "format": "wav"
    }
    
    try:
        print("   🔄 Sending generation request...")
        response = requests.post(
            f"{base_url}/generate", 
            json=test_data,
            timeout=60  # 1 minute timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"   ✅ Audio generated: {result.get('audio_file')}")
                print(f"   💬 Message: {result.get('message')}")
                
                # Test download
                audio_file = result.get('audio_file')
                if audio_file:
                    download_response = requests.get(f"{base_url}/download/{audio_file}")
                    if download_response.status_code == 200:
                        print(f"   ✅ Download successful: {len(download_response.content)} bytes")
                    else:
                        print(f"   ❌ Download failed: {download_response.status_code}")
            else:
                print(f"   ❌ Generation failed: {result.get('message')}")
                print(f"   🔍 Error: {result.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ Request failed: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("   ⏰ Request timed out - this is normal for first generation")
    except Exception as e:
        print(f"   ❌ Generation error: {e}")
    
    print()
    
    # Test 3: Web interface
    print("3. Testing web interface...")
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            print("   ✅ Web interface accessible")
            if "Kokoro TTS" in response.text:
                print("   ✅ Page content loaded correctly")
            else:
                print("   ⚠️ Page content may not be complete")
        else:
            print(f"   ❌ Web interface failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Web interface error: {e}")
    
    print()
    print("🎯 Testing completed!")
    print()
    print("📱 Open your browser and go to: http://localhost:5000")
    print("🎤 Try entering some text and generating audio!")

if __name__ == "__main__":
    test_web_frontend()
