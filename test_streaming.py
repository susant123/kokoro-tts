#!/usr/bin/env python3
"""
Test script for the streaming TTS implementation
"""

import time
import requests
import json
from conversational_ai import ConversationalAI

def test_streaming_performance():
    """Test streaming vs non-streaming performance"""
    print("🧪 Testing Streaming TTS Performance")
    print("=" * 50)
    
    # Initialize AI
    try:
        ai = ConversationalAI()
        print("✅ AI initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize AI: {e}")
        return
    
    # Test texts of different lengths
    test_cases = [
        ("Short text", "Hello, this is a short test message to see how streaming works."),
        ("Medium text", """
        This is a medium-length text to test streaming performance. It contains multiple sentences
        and should be split into several chunks. Each chunk will be processed in parallel, which should
        significantly reduce the time to first audio compared to processing the entire text at once.
        The streaming system intelligently splits text at natural boundaries.
        """),
        ("Long text", """
        This is a comprehensive test of the streaming text-to-speech system that has been implemented
        to improve response times for longer AI responses. The system works by intelligently splitting
        large text responses into smaller, manageable chunks that can be processed in parallel.
        
        The key benefits of this approach are multiple. First, users hear the beginning of the response
        much faster since we don't have to wait for the entire text to be processed. Second, the parallel
        processing of chunks means better utilization of system resources. Third, the intelligent chunking
        respects sentence boundaries and natural speech patterns, ensuring that the audio quality remains high.
        
        The implementation uses Python's ThreadPoolExecutor to process multiple text chunks concurrently.
        Each chunk is sent to the Kokoro TTS engine independently, and the resulting audio files are
        streamed to the frontend as they become available. The frontend then plays these chunks in sequence,
        creating a smooth, continuous audio experience.
        
        This approach should provide significant performance improvements, especially for longer responses
        where the time-to-first-audio can be reduced from several seconds to under a second in many cases.
        The streaming architecture is also designed to gracefully fall back to traditional processing
        if any issues arise with the streaming approach.
        """)
    ]
    
    for test_name, test_text in test_cases:
        print(f"\n🧪 Testing: {test_name}")
        print(f"📝 Text length: {len(test_text)} characters")
        
        # Test regular TTS
        print("\n📞 Regular TTS:")
        start_time = time.time()
        regular_audio = ai.generate_tts_audio(test_text)
        regular_time = time.time() - start_time
        print(f"⏱️ Regular TTS time: {regular_time:.2f}s")
        
        # Test streaming TTS
        print("\n🚀 Streaming TTS:")
        start_time = time.time()
        streaming_chunks = ai.generate_tts_audio_streaming(test_text)
        streaming_time = time.time() - start_time
        
        if streaming_chunks:
            first_chunk_time = min(chunk.duration for chunk in streaming_chunks)
            print(f"⏱️ Total streaming time: {streaming_time:.2f}s")
            print(f"🎯 First chunk ready in: ~{first_chunk_time:.2f}s")
            print(f"📊 Chunks created: {len(streaming_chunks)}")
            print(f"🚀 Performance improvement: {regular_time - first_chunk_time:.2f}s faster first audio")
            
            # Show chunk breakdown
            for i, chunk in enumerate(streaming_chunks):
                preview = chunk.text[:50] + ('...' if len(chunk.text) > 50 else '')
                print(f"   Chunk {i+1}: {chunk.duration:.1f}s - {preview}")
        else:
            print("❌ Streaming TTS failed")
        
        print(f"\n{'='*50}")

def test_web_api():
    """Test the web API streaming endpoint"""
    print("\n🌐 Testing Web API Streaming")
    print("=" * 30)
    
    # Test if server is running
    try:
        response = requests.get("http://localhost:5002/api/status", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not running. Please start the web interface first.")
            return
    except requests.RequestException:
        print("❌ Server is not running. Please start the web interface first.")
        return
    
    # Test streaming API
    test_message = """
    Explain how quantum computing works and what makes it different from classical computing.
    Include information about qubits, superposition, and entanglement in your explanation.
    """
    
    print("📤 Sending test message with streaming enabled...")
    
    start_time = time.time()
    response = requests.post("http://localhost:5002/api/chat", 
                           json={"message": test_message, "streaming": True},
                           timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            total_time = time.time() - start_time
            
            print(f"✅ API Response received in {total_time:.2f}s")
            print(f"🤖 AI Response length: {len(data['ai_response'])} characters")
            
            if data.get("streaming") and data.get("audio_chunks"):
                chunks = data["audio_chunks"]
                print(f"🚀 Streaming enabled: {len(chunks)} chunks")
                
                timing = data.get("timing", {})
                print(f"⏱️ AI time: {timing.get('ai_time', 0):.2f}s")
                print(f"🎤 TTS time: {timing.get('tts_time', 0):.2f}s")
                print(f"🎯 First chunk ready: {timing.get('first_chunk_ready', 0):.2f}s")
                
                # Show chunk info
                for i, chunk in enumerate(chunks):
                    print(f"   Chunk {i+1}: {chunk['duration']:.1f}s - {chunk['audio_file']}")
            else:
                print("📞 Regular (non-streaming) response")
        else:
            print(f"❌ API Error: {data.get('error')}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")

if __name__ == "__main__":
    print("🎵 Kokoro TTS Streaming Performance Test")
    print("=" * 60)
    
    # Test direct streaming implementation
    test_streaming_performance()
    
    # Test web API
    test_web_api()
    
    print("\n🎉 Testing complete!")