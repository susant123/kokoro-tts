# Background Music Feature for Bluetooth Headphones

## Overview
The Kokoro AI Chat interface now includes a background music feature specifically designed to keep Bluetooth headphones connected by providing continuous (but nearly inaudible) audio output.

## Features Added

### 1. Background Audio File
- **File**: `static/background_audio.wav`
- **Duration**: 30 seconds (loops continuously)
- **Volume**: 0.1% of maximum (nearly inaudible)
- **Frequency**: 40Hz with harmonic variations (very low frequency)
- **Sample Rate**: 22,050 Hz (optimized for size)
- **File Size**: ~1.3MB

### 2. Web Interface Controls
- **Enable/Disable Button**: Toggle background music on/off
- **Volume Slider**: Adjust background music volume (0-20%)
- **Visual Feedback**: Button changes color and text when active
- **User Notifications**: System messages when music is enabled/disabled

### 3. Technical Features
- **Auto-Start Protection**: Respects browser autoplay policies
- **User Interaction**: Requires user click/key press to start (browser requirement)
- **Seamless Looping**: No clicks or gaps when audio loops
- **Fade In/Out**: Prevents audio artifacts when looping
- **Low CPU Usage**: Optimized audio generation and playback

## How to Use

### Step 1: Open the Web Interface
```bash
# Start the web server
.venv\Scripts\python.exe conversational_web.py

# Open browser to: http://localhost:5002
```

### Step 2: Enable Background Music
1. Look for "Background Audio" section in the Controls panel
2. Click "Enable BG Music" button
3. Adjust volume slider if needed (default: 5%)
4. The music will start playing in a continuous loop

### Step 3: Test Bluetooth Connection
1. Connect your Bluetooth headphones
2. Enable the background music
3. Leave the page open - your headphones should stay connected
4. The music is designed to be barely audible but sufficient to maintain connection

## Technical Details

### Audio Generation
The background audio is generated using Python with these characteristics:
- **Primary Wave**: 40Hz sine wave (below most human hearing)
- **Harmonic Layers**: Additional waves at 1.2x and 0.8x frequency
- **Amplitude Modulation**: Very low amplitude (0.001 = 0.1%)
- **Fade Curves**: Smooth fade in/out to prevent clicking

### Browser Compatibility
- **Chrome/Edge**: Full support with user interaction requirement
- **Firefox**: Full support with user interaction requirement
- **Safari**: Full support with additional autoplay restrictions
- **Mobile Browsers**: May require additional user interaction

### File Serving
The background audio is served via Flask route:
```python
@app.route('/static/<filename>')
def serve_static(filename):
    # Serves static files including background_audio.wav
```

## Benefits

### For Bluetooth Headphones
1. **Continuous Connection**: Prevents auto-disconnect due to silence
2. **Instant Response**: No reconnection delay when TTS audio plays
3. **Battery Optimization**: Very low power consumption due to minimal volume
4. **Universal Compatibility**: Works with all Bluetooth audio devices

### For User Experience
1. **Seamless Audio**: No interruption in TTS playback
2. **Customizable Volume**: Adjust to your comfort level
3. **Easy Toggle**: Turn on/off as needed
4. **Visual Feedback**: Clear indication of status

## Troubleshooting

### Background Music Won't Start
1. **Browser Autoplay**: Click anywhere on the page first, then try enabling
2. **Volume Check**: Ensure volume slider is above 0
3. **Browser Console**: Check for error messages (F12 → Console)

### Headphones Still Disconnecting
1. **Volume Too Low**: Increase the background music volume slightly
2. **Device Settings**: Check Bluetooth timeout settings on your device
3. **Headphone Model**: Some models have very aggressive power saving

### Performance Issues
1. **Multiple Tabs**: Only enable background music in one tab
2. **System Load**: The feature uses minimal resources, but check system performance
3. **Network**: No network impact - audio file is cached locally

## Advanced Configuration

### Custom Background Audio
To use your own background audio file:
1. Replace `static/background_audio.wav` with your file
2. Ensure it's in WAV format
3. Keep duration under 60 seconds for optimal performance
4. Use very low volume to avoid disturbing the user

### Volume Settings
- **Range**: 0-20% (slider values 0-20)
- **Default**: 5% (optimized for most users)
- **Recommended**: 2-8% depending on headphone sensitivity

## File Structure
```
d:\projects\00\kokoro\
├── static\
│   └── background_audio.wav          # Generated background music file
├── templates\
│   └── chat.html                     # Updated with background audio controls
├── conversational_web.py             # Updated with static file serving
├── generate_background_audio.py      # Script to generate the audio file
└── README.md                        # This documentation
```

## Future Enhancements

### Planned Features
1. **Multiple Background Tracks**: Nature sounds, white noise, etc.
2. **Smart Volume**: Auto-adjust based on system volume
3. **Bluetooth Detection**: Auto-enable when Bluetooth headphones connected
4. **User Preferences**: Save settings in browser localStorage

### Technical Improvements
1. **WebAudio API**: More advanced audio processing
2. **Compression**: Smaller file sizes with better quality
3. **Adaptive Quality**: Adjust based on network conditions

## Integration with Existing Features

The background music feature is fully integrated with:
- ✅ **TTS Audio**: Works alongside conversation audio
- ✅ **Voice Controls**: Independent of voice selection
- ✅ **Auto-play Settings**: Respects existing audio preferences
- ✅ **Conversation Management**: Persists across chat sessions
- ✅ **Mobile Compatibility**: Works on mobile devices

---

*This feature was specifically designed to solve the Bluetooth headphone disconnection issue while maintaining an excellent user experience. The background audio is intentionally nearly inaudible but sufficient to keep audio devices active.*