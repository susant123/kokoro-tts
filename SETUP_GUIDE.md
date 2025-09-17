# Kokoro TTS Local Project Setup

## Project Overview

This is a local installation of Kokoro TTS, a high-quality text-to-speech CLI tool that supports multiple languages and voices.

## Installation Status

✅ Repository cloned successfully  
✅ Python virtual environment created  
✅ All Python dependencies installed  
⚠️ Model files downloaded but may need verification

## Project Structure

```
kokoro/
├── .venv/                  # Python virtual environment
├── kokoro-tts             # Main TTS script
├── kokoro-v1.0.onnx       # AI model file (ONNX format)
├── voices-v1.0.bin        # Voice data file
├── sample.txt             # Sample text file for testing
├── requirements.txt       # Python dependencies
├── README.md             # Original project documentation
└── ...                   # Other project files
```

## Quick Start

### 1. Activate Virtual Environment (if needed)

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Basic Usage Examples

#### Convert text file to audio:

```powershell
python kokoro-tts sample.txt output.wav --voice af_sarah
```

#### Stream audio directly (no file output):

```powershell
python kokoro-tts sample.txt --stream --voice af_sarah
```

#### List available voices:

```powershell
python kokoro-tts --help-voices
```

#### List supported languages:

```powershell
python kokoro-tts --help-languages
```

### 3. Advanced Features

#### Voice Blending (mix two voices):

```powershell
python kokoro-tts sample.txt output.wav --voice "af_sarah:60,am_adam:40"
```

#### Process EPUB books:

```powershell
python kokoro-tts book.epub --split-output ./chapters/ --format mp3
```

#### Adjust speech speed:

```powershell
python kokoro-tts sample.txt output.wav --speed 1.2 --voice af_sarah
```

#### Process from stdin:

```powershell
echo "Hello World" | python kokoro-tts /dev/stdin --stream
```

## Supported Voices

### English (US) Female:

- af_alloy, af_aoede, af_bella, af_heart, af_jessica, af_kore, af_nicole, af_nova, af_river, af_sarah, af_sky

### English (US) Male:

- am_adam, am_echo, am_eric, am_fenrir, am_liam, am_michael, am_onyx, am_puck

### English (GB):

- bf_alice, bf_emma, bf_isabella, bf_lily, bm_daniel, bm_fable, bm_george, bm_lewis

### Other Languages:

- French: ff_siwis
- Italian: if_sara, im_nicola
- Japanese: jf_alpha, jf_gongitsune, jf_nezumi, jf_tebukuro, jm_kumo
- Chinese: zf_xiaobei, zf_xiaoni, zf_xiaoxiao, zf_xiaoyi, zm_yunjian, zm_yunxi, zm_yunxia, zm_yunyang

## Troubleshooting

### If you encounter model loading errors:

1. Try downloading the model files again from the official sources
2. Check if the files are complete and not corrupted
3. Ensure you have the latest version of the dependencies

### Model File Sources:

- Model: https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
- Voices: https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin

## Features

- Multiple language and voice support
- Voice blending with customizable weights
- EPUB, PDF and TXT file input support
- Standard input (stdin) and pipe support
- Streaming audio playback
- Split output into chapters
- Adjustable speech speed
- WAV and MP3 output formats
- Chapter merging capability
- Detailed debug output option

## Requirements

- Python 3.12 (recommended) or compatible version
- All dependencies installed via pip (already done)

## Next Steps

1. Test the installation with a simple command
2. If model errors persist, try downloading the model files again
3. Explore the various voice options and features
4. Create your own text files for TTS conversion

## Links

- [Official Repository](https://github.com/nazdridoy/kokoro-tts)
- [Kokoro Model on HuggingFace](https://huggingface.co/hexgrad/Kokoro-82M)
- [Kokoro-ONNX Repository](https://github.com/thewh1teagle/kokoro-onnx)
