import soundfile as sf
import sounddevice as sd
from kokoro_onnx import Kokoro
import os
import sys
import itertools
import threading
import time
import signal
from ebooklib import epub
from bs4 import BeautifulSoup
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module='ebooklib')
warnings.filterwarnings("ignore", category=FutureWarning, module='ebooklib')

# Global flag to stop the spinner and audio
stop_spinner = False
stop_audio = False

def spinning_wheel(message="Processing...", progress=None):
    spinner = itertools.cycle(['|', '/', '-', '\\'])
    while not stop_spinner:
        if progress is not None:
            sys.stdout.write(f'\r{message} {progress}% {next(spinner)}')
        else:
            sys.stdout.write(f'\r{message} {next(spinner)}')
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\r')
    sys.stdout.flush()

def list_available_voices(kokoro):
    voices = list(kokoro.get_voices())
    print("Available voices:")
    for idx, voice in enumerate(voices):
        print(f"{idx + 1}. {voice}")
    return voices

def extract_text_from_epub(epub_file):
    book = epub.read_epub(epub_file)
    full_text = ""
    for item in book.get_items():
        # Check if the item is a document based on mime type (e.g., text/html, application/xhtml+xml)
        if item.get_type() == 9:  # 9 corresponds to DOCUMENT in ebooklib
            soup = BeautifulSoup(item.get_body_content(), "html.parser")  # Use get_body_content() here
            full_text += soup.get_text()
    return full_text

def chunk_text(text, chunk_size=1000):
    """Split text into chunks at sentence boundaries."""
    words = text.split()
    chunks = []
    current_chunk = []
    current_size = 0
    
    for word in words:
        current_chunk.append(word)
        current_size += len(word) + 1  # +1 for space
        
        if current_size >= chunk_size and word[-1] in '.!?':
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_size = 0
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def convert_text_to_audio(input_file, output_file=None, voice="af_sarah", speed=1.0, lang="en-us", stream=False):
    global stop_spinner
    # Load Kokoro model
    try:
        kokoro = Kokoro("kokoro-v0_19.onnx", "voices.json")
    except Exception as e:
        print(f"Error loading Kokoro model: {e}")
        sys.exit(1)
    
    # List available voices and choose one
    voices = list_available_voices(kokoro)
    try:
        voice_choice = int(input("Choose a voice by number: ")) - 1
        if voice_choice < 0 or voice_choice >= len(voices):
            raise ValueError("Invalid choice")
        voice = voices[voice_choice]
    except (ValueError, IndexError):
        print("Invalid choice. Using default voice.")
    
    # Read the input file (handle .txt or .epub)
    if input_file.endswith('.epub'):
        text = extract_text_from_epub(input_file)
    else:
        with open(input_file, 'r', encoding='utf-8') as file:
            text = file.read()

    # Handle spinner when creating non-stream audio
    if not stream and output_file:
        stop_spinner = False
        spinner_thread = threading.Thread(target=spinning_wheel, args=("Creating audio file...",))
        spinner_thread.start()

    if stream or not output_file:
        import asyncio
        asyncio.run(stream_audio(kokoro, text, voice, speed, lang))
    else:
        samples, sample_rate = kokoro.create(
            text, voice=voice, speed=speed, lang=lang
        )
        # Save the generated audio to the specified output file
        sf.write(output_file, samples, sample_rate)
        print(f"Created {output_file}")
    
    # Stop spinner after the process completes
    stop_spinner = True
    if not stream and output_file:
        spinner_thread.join()

async def stream_audio(kokoro, text, voice, speed, lang):
    global stop_spinner, stop_audio
    stop_spinner = False
    stop_audio = False
    spinner_thread = threading.Thread(target=spinning_wheel)
    spinner_thread.start()

    print("Streaming audio...")
    chunks = chunk_text(text)
    for chunk in chunks:
        if stop_audio:
            break
        async for samples, sample_rate in kokoro.create_stream(
            chunk, voice=voice, speed=speed, lang=lang
        ):
            if stop_audio:
                break
            sd.play(samples, sample_rate)
            sd.wait()

    stop_spinner = True
    spinner_thread.join()
    print("Streaming completed.")

def handle_ctrl_c(signum, frame):
    global stop_spinner, stop_audio
    print("\nCtrl+C detected, stopping...")
    stop_spinner = True
    stop_audio = True
    sys.exit(0)

# Register the signal handler for SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, handle_ctrl_c)

def print_usage():
    print("""
Usage: python main.py <input_text_file> [<output_audio_file>] [options]

Options:
    --stream        Stream audio instead of saving to file
    --speed <float> Set speech speed (default: 1.0)
    --lang <str>    Set language (default: en-us)

Example:
    python main.py input.txt output.wav --speed 1.2 --lang en-us
    python main.py input.epub --stream
    """)

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help']:
        print_usage()
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else None
    stream = '--stream' in sys.argv
    speed = 1.0  # default speed
    lang = "en-us"  # default language
    
    # Parse optional arguments
    for i, arg in enumerate(sys.argv):
        if arg == '--speed' and i + 1 < len(sys.argv):
            try:
                speed = float(sys.argv[i + 1])
            except ValueError:
                print("Error: Speed must be a number")
                sys.exit(1)
        elif arg == '--lang' and i + 1 < len(sys.argv):
            lang = sys.argv[i + 1]
    
    # Ensure the input file exists
    if not os.path.isfile(input_file):
        print(f"Error: The file {input_file} does not exist.")
        sys.exit(1)
    
    # Ensure the output file has a proper extension if not streaming
    if output_file and not output_file.endswith(('.wav', '.mp3')):
        print("Error: Output file must have .wav or .mp3 extension.")
        sys.exit(1)
    
    # Convert text to audio or stream
    convert_text_to_audio(input_file, output_file, stream=stream, speed=speed, lang=lang)

