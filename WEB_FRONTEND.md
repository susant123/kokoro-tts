# 🎤 Kokoro TTS Web Frontend

A modern, user-friendly web interface for the Kokoro TTS (Text-to-Speech) system.

## ✨ Features

- **🌐 Web-Based Interface**: No command-line knowledge required
- **🎭 Multiple Voices**: Support for 25+ voices in multiple languages
- **🌍 Multi-Language**: English (US/GB), French, Italian, Japanese, Chinese
- **⚡ Real-Time Processing**: Convert text to speech instantly
- **🎛️ Advanced Controls**: Adjust speech speed, choose audio format
- **📱 Responsive Design**: Works on desktop, tablet, and mobile
- **🔊 Built-in Audio Player**: Play generated audio directly in browser
- **💾 Download Support**: Save audio files in WAV or MP3 format
- **🧹 Auto Cleanup**: Automatic temporary file management

## 🚀 Quick Start

### 1. Start the Web Server

**Option A: Using Batch File (Windows)**

```cmd
start_web.bat
```

**Option B: Using PowerShell**

```powershell
.\start_web.ps1
```

**Option C: Manual Start**

```cmd
.venv\Scripts\python.exe app.py
```

### 2. Open Your Browser

Navigate to: **http://localhost:5000**

### 3. Use the Interface

1. **Enter Text**: Type or paste your text (up to 10,000 characters)
2. **Choose Voice**: Select from 25+ available voices
3. **Adjust Settings**: Set language, speed (0.5x - 2.0x), and format
4. **Generate**: Click "Generate Speech"
5. **Listen & Download**: Play in browser or download the audio file

## 🎭 Available Voices

### English (US) - Female

- Sarah, Bella, Nova, Jessica, Nicole, River, Sky, and more

### English (US) - Male

- Adam, Liam, Michael, Eric, Echo, Onyx, and more

### English (GB)

- Alice, Emma, Isabella, Daniel, George, Lewis

### Other Languages

- **French**: Siwis
- **Italian**: Sara, Nicola
- **Japanese**: Alpha, Gongitsune, Kumo
- **Chinese**: Xiaobei, Yunjian, Yunxi

## ⚙️ Configuration

The web frontend automatically detects your Kokoro TTS installation. Make sure:

- ✅ Virtual environment is activated
- ✅ Model files are downloaded (`kokoro-v1.0.onnx`, `voices-v1.0.bin`)
- ✅ All dependencies are installed

## 🔧 Technical Details

### Backend

- **Framework**: Flask (Python)
- **TTS Engine**: Kokoro TTS CLI
- **Audio Processing**: WAV/MP3 output
- **File Management**: Automatic cleanup

### Frontend

- **Framework**: Bootstrap 5
- **Icons**: Font Awesome
- **Responsive**: Mobile-friendly design
- **Audio**: HTML5 audio player

### API Endpoints

- `GET /` - Main interface
- `POST /generate` - Generate audio from text
- `GET /download/<filename>` - Download audio file
- `GET /status` - System status check
- `GET /cleanup` - Clean temporary files

## 📁 File Structure

```
kokoro/
├── app.py                 # Flask web application
├── templates/
│   └── index.html        # Main web interface
├── static/               # Static assets (CSS, JS, images)
├── temp_audio/          # Temporary audio files (auto-created)
├── start_web.bat        # Windows launcher
├── start_web.ps1        # PowerShell launcher
└── WEB_FRONTEND.md      # This documentation
```

## 🛠️ Troubleshooting

### Common Issues

**❌ "System not ready" error**

- Check that model files exist: `kokoro-v1.0.onnx` and `voices-v1.0.bin`
- Verify virtual environment is properly set up

**❌ "Connection error"**

- Make sure the Flask server is running
- Check firewall settings for port 5000

**❌ Audio generation fails**

- Verify text is not empty and under 10,000 characters
- Check that Python dependencies are installed
- Look at server console for error messages

**❌ Slow generation**

- Long texts take more time to process
- Try shorter text segments
- Check system resources (CPU/RAM)

### Getting Help

1. Check the server console for error messages
2. Verify system status at: http://localhost:5000/status
3. Test CLI functionality first: `python kokoro-tts sample.txt --stream`
4. Check the main project documentation

## 🔒 Security Notes

- The web server runs on localhost by default (secure)
- Temporary files are automatically cleaned up
- No user data is permanently stored
- Audio files are deleted after 1 hour

## 🎯 Usage Tips

- **Optimal Text Length**: 100-1000 characters for best performance
- **Voice Selection**: Try different voices to find your preference
- **Speed Adjustment**: 1.0x is normal, 0.8x is slower, 1.2x is faster
- **Format Choice**: WAV for quality, MP3 for smaller files
- **Mobile Use**: Interface is fully responsive and touch-friendly

## 📈 Future Enhancements

- Voice blending support (combine multiple voices)
- Batch processing for multiple files
- EPUB/PDF upload support
- Voice preview samples
- Advanced audio settings
- User preferences storage

---

**Enjoy using Kokoro TTS Web Frontend! 🎉**
