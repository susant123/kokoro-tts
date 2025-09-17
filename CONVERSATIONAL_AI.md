# 🤖 Kokoro Conversational AI

A complete conversational AI system that combines **Ollama (Llama 3.2)** with **GPU-accelerated Kokoro TTS** for natural conversations with voice synthesis.

## ✨ Features

- **🧠 Smart Conversations**: Powered by Llama 3.2 via Ollama
- **🎤 Natural Voice**: GPU-accelerated Kokoro TTS with 25+ voices
- **🌐 Web Interface**: Modern, responsive chat interface
- **💬 CLI Mode**: Terminal-based conversational experience
- **🔄 Context Awareness**: Maintains conversation history and context
- **⚡ High Performance**: Sub-second TTS generation with model preloading
- **📊 Statistics**: Real-time performance metrics and conversation analytics
- **💾 Conversation Export**: Save and load conversation histories

## 🚀 Quick Start

### 1. Start Ollama (Required)

Make sure Ollama is running with Llama 3.2:

```bash
# Start Ollama service
ollama serve

# In another terminal, ensure Llama 3.2 is available
ollama list
```

### 2. Launch Conversational AI

**Option A: Web Interface (Recommended)**
```bash
# Using batch file
start_conversational_ai.bat

# Or using PowerShell
.\start_conversational_ai.ps1

# Or manually
.venv\Scripts\python.exe conversational_web.py
```

Access at: **http://localhost:5002**

**Option B: CLI Mode**
```bash
.venv\Scripts\python.exe conversational_ai.py
```

## 🎭 Available Voices

### 🇺🇸 English (US) - Female
- **af_sarah**: Sarah (Professional, Clear) ⭐ *Default*
- **af_bella**: Bella (Warm, Friendly)
- **af_nova**: Nova (Energetic, Young)
- **af_jessica**: Jessica (Mature, Wise)
- **af_river**: River (Soft, Gentle)
- **af_sky**: Sky (Bright, Cheerful)

### 🇺🇸 English (US) - Male
- **am_adam**: Adam (Deep, Confident)
- **am_liam**: Liam (Young, Casual)
- **am_michael**: Michael (Professional, Clear)
- **am_eric**: Eric (Friendly, Approachable)
- **am_echo**: Echo (Mysterious, Dramatic)
- **am_onyx**: Onyx (Strong, Authoritative)

### 🇬🇧 English (GB)
- **bf_alice**: Alice (British, Elegant)
- **bf_emma**: Emma (British, Warm)
- **bm_daniel**: Daniel (British, Gentleman)
- **bm_george**: George (British, Distinguished)

## 🌐 Web Interface Features

### Chat Interface
- **Real-time messaging** with AI responses
- **Audio playback** of AI responses (auto-play toggle)
- **Voice selection** with live preview
- **Typing indicators** and status monitoring
- **Responsive design** for desktop and mobile

### Controls Panel
- **Voice changer**: Switch between 25+ voices instantly
- **Auto-play toggle**: Enable/disable automatic audio playback
- **Clear conversation**: Reset chat history
- **Save conversation**: Export chat to JSON file
- **Real-time statistics**: Response times, message counts, etc.

### Performance Metrics
- **AI Response Time**: How long Llama takes to generate text
- **TTS Generation Time**: GPU-accelerated speech synthesis time
- **Total Response Time**: End-to-end conversation latency
- **Average Performance**: Running statistics across conversation

## 💬 CLI Mode Commands

When using the terminal interface:

```bash
# Chat normally
You: Hello, how are you today?

# Special commands
voice <name>     # Change TTS voice (e.g., "voice am_adam")
voices           # List all available voices
stats           # Show conversation statistics  
save            # Save conversation to JSON
mute            # Toggle audio playback on/off
quit/exit       # End conversation and save
```

## ⚡ Performance Optimization

### GPU Acceleration Status
- ✅ **TTS Model Preloaded**: Instant voice generation
- ✅ **GPU Memory Optimized**: ~400MB GPU RAM usage
- ✅ **Fallback System**: CLI fallback if direct API fails
- ⚠️ **CUDA Libraries**: Some warnings present but system functional

### Typical Performance (RTX 4090)
- **AI Response**: ~2.0-3.0s (depends on response complexity)
- **TTS Generation**: ~0.6s (with preloaded model)
- **Total Response**: ~2.6-3.6s (including audio generation)

## 🔧 Configuration

### Environment Variables
```bash
# GPU acceleration (automatically set)
ONNX_PROVIDER=CUDAExecutionProvider
```

### Ollama Settings
- **Default Model**: `llama3.2:latest`
- **Host**: `http://localhost:11434`
- **Context Window**: Maintains last 10 messages for context

### TTS Settings
- **Default Voice**: `af_sarah` (Sarah - Professional, Clear)
- **Sample Rate**: 24kHz
- **Audio Format**: WAV (uncompressed)
- **Speed**: 1.0x (adjustable in code)

## 📁 File Structure

```
kokoro/
├── conversational_ai.py      # CLI conversational interface
├── conversational_web.py     # Web interface Flask app
├── templates/
│   └── chat.html             # Web chat interface
├── temp_conversations/       # Audio files and conversation exports
├── start_conversational_ai.bat  # Windows launcher
├── start_conversational_ai.ps1  # PowerShell launcher
└── CONVERSATIONAL_AI.md      # This documentation
```

## 🎯 Usage Examples

### Web Interface
1. Open http://localhost:5002
2. Select your preferred voice from the dropdown
3. Type a message and press Enter
4. Listen to the AI's response with synthesized speech
5. Toggle auto-play, change voices, or save conversations as needed

### CLI Interface
```
👤 You: What's the weather like today?
🤖 AI (2.1s): I don't have access to real-time weather data, but I'd be happy to discuss...
🎤 Generating speech...
✅ Speech generated (0.6s)
🔊 Playing audio...
⏱️ (AI: 2.1s, TTS: 0.6s, Total: 2.7s)
```

## 🔍 Troubleshooting

### Ollama Connection Issues
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if not running
ollama serve

# Verify Llama 3.2 is available
ollama list
```

### TTS Generation Issues
- **Direct API Errors**: System automatically falls back to CLI method
- **CUDA Warnings**: Non-fatal, GPU acceleration still functional
- **Audio Playback**: Check system volume and audio device settings

### Web Interface Issues
```bash
# Check if port 5002 is available
netstat -an | findstr :5002

# Access logs in terminal running conversational_web.py
```

## 📈 Future Enhancements

### Planned Features
- **🎵 Voice Cloning**: Custom voice training from audio samples
- **🌍 Multi-language Support**: Expand beyond English voices
- **🔊 Voice Mixing**: Blend multiple voices for unique sounds
- **📱 Mobile App**: Native mobile application
- **🎮 Interactive Modes**: Gaming, storytelling, educational modes

### Advanced Integration
- **📚 RAG Support**: Document-based conversations
- **🎨 Visual Responses**: Image generation integration
- **🔗 API Endpoints**: RESTful API for external integrations
- **👥 Multi-user**: Concurrent conversation support

---

## 🎉 Enjoy Your Conversational AI!

You now have a powerful conversational AI system that combines the intelligence of Llama 3.2 with the natural-sounding voice of Kokoro TTS, all optimized for your RTX 4090 GPU.

**Start chatting and experience the future of human-AI interaction! 🚀**