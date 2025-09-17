#!/usr/bin/env python3
"""
Voice Samples Validator
Quick test to verify all voice samples are accessible
"""

import requests
import json
import time

def test_voice_samples_api():
    """Test the voice samples API endpoint"""
    print("🧪 Testing Voice Samples API")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:5000/voice_samples")
        if response.status_code == 200:
            data = response.json()
            print("✅ API endpoint working")
            print(f"📝 Sample text: '{data.get('sample_text', 'N/A')}'")
            
            total_voices = 0
            for category, voices in data.get('categories', {}).items():
                count = len(voices)
                total_voices += count
                print(f"📂 {category}: {count} voices")
                
                # Test first voice in category
                if voices:
                    first_voice = list(voices.items())[0]
                    voice_id, voice_data = first_voice
                    print(f"   🎤 Testing {voice_data['name']} ({voice_data['size_kb']} KB)")
            
            print(f"\n📊 Total voices: {total_voices}")
            return True
            
        else:
            print(f"❌ API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 Error: {e}")
        return False

def test_sample_accessibility():
    """Test that sample files are accessible via HTTP"""
    print("\n🌐 Testing Sample File Accessibility")
    print("=" * 40)
    
    try:
        # Get samples data
        response = requests.get("http://localhost:5000/voice_samples")
        data = response.json()
        
        test_urls = []
        for category, voices in data.get('categories', {}).items():
            for voice_id, voice_data in voices.items():
                test_urls.append((voice_data['name'], voice_data['url']))
                if len(test_urls) >= 3:  # Test first 3 voices only
                    break
            if len(test_urls) >= 3:
                break
        
        print(f"🔍 Testing {len(test_urls)} sample files...")
        
        accessible = 0
        for voice_name, url in test_urls:
            try:
                full_url = f"http://localhost:5000{url}"
                response = requests.head(full_url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ {voice_name}: Accessible")
                    accessible += 1
                else:
                    print(f"❌ {voice_name}: Status {response.status_code}")
            except Exception as e:
                print(f"❌ {voice_name}: Error - {e}")
        
        print(f"\n📊 Accessible: {accessible}/{len(test_urls)}")
        return accessible == len(test_urls)
        
    except Exception as e:
        print(f"💥 Error: {e}")
        return False

def test_main_page():
    """Test that the main page loads correctly"""
    print("\n🏠 Testing Main Page")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:5000/")
        if response.status_code == 200:
            content = response.text
            
            # Check for voice samples section
            if 'voice-samples-section' in content:
                print("✅ Main page loads with voice samples section")
            else:
                print("⚠️  Main page loads but voice samples section not found")
            
            # Check for required JavaScript
            if 'loadVoiceSamples' in content:
                print("✅ Voice samples JavaScript included")
            else:
                print("❌ Voice samples JavaScript missing")
            
            return True
        else:
            print(f"❌ Page load error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 Error: {e}")
        return False

def main():
    print("🎭 Kokoro TTS Voice Samples Validator")
    print("=" * 50)
    print("Testing the new voice samples feature...")
    print()
    
    # Wait a moment for server to be ready
    time.sleep(1)
    
    # Run tests
    tests = [
        ("API Endpoint", test_voice_samples_api),
        ("File Accessibility", test_sample_accessibility), 
        ("Main Page", test_main_page)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            time.sleep(0.5)  # Brief pause between tests
        except Exception as e:
            print(f"💥 {test_name} failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Validation Complete!")
    print(f"📊 Tests passed: {passed}/{len(tests)}")
    
    if passed == len(tests):
        print("✅ All systems working! Voice samples ready!")
        print("🌐 Visit http://localhost:5000 to see the samples")
    else:
        print("⚠️  Some tests failed. Check the output above.")
    
    print("\n🎯 Next steps:")
    print("1. Open http://localhost:5000 in your browser")
    print("2. Check the 'Voice Samples' section")
    print("3. Play different voice samples")
    print("4. Click 'Use This Voice' to select a voice")
    print("5. Generate TTS with your chosen voice!")

if __name__ == "__main__":
    main()
