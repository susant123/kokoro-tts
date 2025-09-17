"""
Generate a very low volume background audio file to keep Bluetooth headphones connected
"""
import numpy as np
import soundfile as sf
import os

def generate_background_audio():
    """Generate a very quiet background audio file"""
    # Audio parameters
    sample_rate = 22050  # Lower sample rate for smaller file
    duration = 30  # 30 seconds, will loop
    frequency = 40  # Very low frequency (almost inaudible)
    
    # Generate time array
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Generate a very quiet sine wave with some variation
    amplitude = 0.001  # Extremely low volume (0.1% of max)
    
    # Create a gentle, varying tone
    wave1 = amplitude * np.sin(2 * np.pi * frequency * t)
    wave2 = amplitude * 0.5 * np.sin(2 * np.pi * (frequency * 1.2) * t)
    wave3 = amplitude * 0.3 * np.sin(2 * np.pi * (frequency * 0.8) * t)
    
    # Combine waves for a more natural sound
    audio = wave1 + wave2 + wave3
    
    # Apply fade in/out to avoid clicks when looping
    fade_samples = int(0.1 * sample_rate)  # 0.1 second fade
    
    # Fade in
    audio[:fade_samples] *= np.linspace(0, 1, fade_samples)
    # Fade out
    audio[-fade_samples:] *= np.linspace(1, 0, fade_samples)
    
    # Ensure audio is normalized to prevent clipping
    audio = audio / np.max(np.abs(audio)) * amplitude
    
    # Save to static directory
    static_dir = 'static'
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    
    output_file = os.path.join(static_dir, 'background_audio.wav')
    sf.write(output_file, audio, sample_rate)
    
    print(f"✅ Background audio generated: {output_file}")
    print(f"📊 Duration: {duration}s, Sample Rate: {sample_rate}Hz, Volume: {amplitude*100:.3f}%")
    print(f"📁 File size: {os.path.getsize(output_file)} bytes")
    
    return output_file

if __name__ == "__main__":
    generate_background_audio()