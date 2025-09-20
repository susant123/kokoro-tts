"""
Kokoro TTS + Ollama Conversational AI
Interactive conversational system with Llama 3.2 and GPU-accelerated TTS
"""

import os
import time
import json
import uuid
import threading
import requests
import re
import concurrent.futures
import asyncio
import queue
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from kokoro_onnx import Kokoro
import soundfile as sf
import sounddevice as sd
import numpy as np

# Enable GPU acceleration
os.environ["ONNX_PROVIDER"] = "CUDAExecutionProvider"

@dataclass
class ConversationMessage:
    """Represents a single message in the conversation"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    audio_file: Optional[str] = None
    voice: Optional[str] = None
    audio_chunks: Optional[List[str]] = None  # For streaming audio chunks

@dataclass
class AudioChunk:
    """Represents a chunk of audio for streaming"""
    chunk_id: int
    text: str
    audio_file: str
    duration: float
    is_final: bool = False

class ConversationalAI:
    """Main conversational AI system"""
    
    def __init__(self, 
                 ollama_host: str = "http://localhost:11434",
                 ollama_model: str = "llama3.2:latest",
                 tts_voice: str = "af_sarah",
                 tts_speed: float = 1.0):
        
        self.ollama_host = ollama_host
        self.ollama_model = ollama_model
        self.tts_voice = tts_voice
        self.tts_speed = tts_speed
        
        # Initialize TTS model with GPU acceleration
        print("🔄 Loading Kokoro TTS model with GPU acceleration...")
        self.kokoro = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")
        print("✅ TTS model loaded successfully!")
        
        # Conversation state
        self.conversation_history: List[ConversationMessage] = []
        self.conversation_id = str(uuid.uuid4())
        
        # Audio settings
        self.temp_dir = "temp_conversations"
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Available voices
        self.voices = {
            # Female voices
            "af_sarah": "Sarah (Professional, Clear)",
            "af_bella": "Bella (Warm, Friendly)", 
            "af_nova": "Nova (Energetic, Young)",
            "af_jessica": "Jessica (Mature, Wise)",
            "af_river": "River (Soft, Gentle)",
            "af_sky": "Sky (Bright, Cheerful)",
            
            # Male voices
            "am_adam": "Adam (Deep, Confident)",
            "am_liam": "Liam (Young, Casual)",
            "am_michael": "Michael (Professional, Clear)",
            "am_eric": "Eric (Friendly, Approachable)",
            "am_echo": "Echo (Mysterious, Dramatic)",
            "am_onyx": "Onyx (Strong, Authoritative)",
            
            # British voices
            "bf_alice": "Alice (British, Elegant)",
            "bf_emma": "Emma (British, Warm)",
            "bm_daniel": "Daniel (British, Gentleman)",
            "bm_george": "George (British, Distinguished)"
        }
        
        print(f"🎤 TTS Voice: {self.voices.get(self.tts_voice, self.tts_voice)}")
        print(f"🧠 AI Model: {self.ollama_model}")
    
    def test_ollama_connection(self) -> bool:
        """Test if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Ollama connection failed: {e}")
            return False
    
    def get_ai_response(self, user_message: str, context: str = None) -> str:
        """Get response from Ollama"""
        try:
            # Prepare conversation context
            messages = []
            
            # Add system context if provided
            if context:
                messages.append({
                    "role": "system",
                    "content": context
                })
            
            # Add conversation history
            for msg in self.conversation_history[-10:]:  # Last 10 messages for context
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            # Add current user message
            messages.append({
                "role": "user", 
                "content": user_message
            })
            
            # Make request to Ollama
            payload = {
                "model": self.ollama_model,
                "messages": messages,
                "stream": False
            }
            
            response = requests.post(
                f"{self.ollama_host}/api/chat",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["message"]["content"]
            else:
                return f"Error: Ollama returned status {response.status_code}"
                
        except Exception as e:
            return f"Error communicating with AI: {str(e)}"
    
    def clean_text_for_tts(self, text: str) -> str:
        """Clean text by removing markdown formatting characters for TTS"""
        import re
        
        # Remove code blocks (triple backticks)
        text = re.sub(r'```[\s\S]*?```', '', text)
        
        # Remove inline code (single backticks)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        
        # Remove headers (# ## ###)
        text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
        
        # Remove bold formatting (**text**)
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        
        # Remove italic formatting (*text*)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        
        # Remove blockquote markers (>)
        text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
        
        # Clean up bullet points and numbered lists
        text = re.sub(r'^[-*+]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
        
        # Remove extra whitespace and line breaks
        text = re.sub(r'\n+', ' ', text)  # Replace multiple newlines with single space
        text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single space
        text = text.strip()
        
        return text
    
    def split_text_for_streaming(self, text: str, max_chunk_size: int = 200) -> List[str]:
        """
        Intelligently split text into chunks suitable for streaming TTS.
        Respects sentence boundaries, paragraphs, and natural speech pauses.
        """
        # Clean the text first
        clean_text = self.clean_text_for_tts(text).strip()
        if not clean_text:
            return []
        
        chunks = []
        
        # First, split by major boundaries (paragraphs, line breaks)
        major_sections = re.split(r'\n\s*\n|\n\s*[-*•]\s*|\n\d+\.\s*', clean_text)
        
        for section in major_sections:
            section = section.strip()
            if not section:
                continue
                
            # If section is small enough, add it as a chunk
            if len(section) <= max_chunk_size:
                chunks.append(section)
                continue
            
            # Split by sentences, but keep related sentences together
            sentences = self._split_into_sentences(section)
            
            current_chunk = ""
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                
                # If adding this sentence would exceed limit, save current chunk
                if current_chunk and len(current_chunk + " " + sentence) > max_chunk_size:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence
                else:
                    if current_chunk:
                        current_chunk += " " + sentence
                    else:
                        current_chunk = sentence
                
                # If single sentence is too long, split it further
                if len(current_chunk) > max_chunk_size * 1.5:  # Allow some flexibility
                    sub_chunks = self._split_long_sentence(current_chunk, max_chunk_size)
                    chunks.extend(sub_chunks[:-1])  # Add all but last
                    current_chunk = sub_chunks[-1] if sub_chunks else ""
            
            # Add remaining text
            if current_chunk:
                chunks.append(current_chunk.strip())
        
        # Clean up empty chunks and ensure reasonable minimum length
        final_chunks = []
        for chunk in chunks:
            chunk = chunk.strip()
            if chunk and len(chunk) >= 5:  # Minimum chunk length
                final_chunks.append(chunk)
        
        return final_chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences, handling common abbreviations"""
        # Common abbreviations that shouldn't trigger sentence splits
        abbreviations = r'\b(?:Dr|Mr|Mrs|Ms|Prof|Sr|Jr|Inc|Ltd|Corp|Co|etc|vs|i\.e|e\.g|a\.m|p\.m|U\.S|U\.K)\.'
        
        # Temporarily replace abbreviations
        temp_text = re.sub(abbreviations, lambda m: m.group().replace('.', '§TEMP§'), text, flags=re.IGNORECASE)
        
        # Split on sentence boundaries
        sentences = re.split(r'[.!?]+\s+', temp_text)
        
        # Restore abbreviations and clean up
        sentences = [s.replace('§TEMP§', '.').strip() for s in sentences if s.strip()]
        
        return sentences
    
    def _split_long_sentence(self, sentence: str, max_size: int) -> List[str]:
        """Split a long sentence at natural pause points"""
        if len(sentence) <= max_size:
            return [sentence]
        
        # Try to split at commas, semicolons, or conjunctions
        pause_patterns = [
            r',\s+(?=\w)',  # Commas
            r';\s+',        # Semicolons  
            r'\s+(?:and|but|or|however|therefore|moreover|furthermore|meanwhile|consequently)\s+',  # Conjunctions
            r'\s+(?:which|that|who|where|when)\s+',  # Relative pronouns
        ]
        
        for pattern in pause_patterns:
            parts = re.split(f'({pattern})', sentence)
            if len(parts) > 1:
                chunks = []
                current = ""
                
                for i, part in enumerate(parts):
                    if i % 2 == 0:  # Text part
                        if current and len(current + part) > max_size:
                            if current:
                                chunks.append(current.strip())
                            current = part
                        else:
                            current += part
                    else:  # Separator part
                        current += part
                
                if current:
                    chunks.append(current.strip())
                
                # If we got reasonable chunks, return them
                if len(chunks) > 1 and all(len(c) <= max_size * 1.2 for c in chunks):
                    return [c for c in chunks if c.strip()]
        
        # Last resort: split by words
        words = sentence.split()
        chunks = []
        current = ""
        
        for word in words:
            if current and len(current + " " + word) > max_size:
                if current:
                    chunks.append(current.strip())
                current = word
            else:
                if current:
                    current += " " + word
                else:
                    current = word
        
        if current:
            chunks.append(current.strip())
        
        return chunks
    
    def generate_tts_audio_streaming(self, text: str, voice: str = None) -> List[AudioChunk]:
        """
        Generate TTS audio with streaming support - processes chunks in parallel
        and returns them as they become available for immediate playback.
        """
        if voice is None:
            voice = self.tts_voice
        
        # Split text into chunks
        text_chunks = self.split_text_for_streaming(text)
        if not text_chunks:
            return []
        
        print(f"🎤 Streaming TTS: Split into {len(text_chunks)} chunks")
        for i, chunk in enumerate(text_chunks):
            preview = chunk[:50] + ('...' if len(chunk) > 50 else '')
            print(f"  Chunk {i+1}: {preview}")
        
        audio_chunks = []
        start_time = time.time()
        
        # Use ThreadPoolExecutor for parallel processing
        max_workers = min(4, len(text_chunks))  # Limit concurrent TTS processes
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all chunks for processing
            future_to_chunk = {
                executor.submit(self._generate_chunk_audio, chunk_text, i, voice): i 
                for i, chunk_text in enumerate(text_chunks)
            }
            
            # Process chunks as they complete
            completed_count = 0
            
            for future in concurrent.futures.as_completed(future_to_chunk):
                chunk_index = future_to_chunk[future]
                
                try:
                    audio_chunk = future.result()
                    if audio_chunk:
                        audio_chunks.append(audio_chunk)
                        completed_count += 1
                        
                        elapsed = time.time() - start_time
                        print(f"✅ Chunk {chunk_index + 1}/{len(text_chunks)} ready ({elapsed:.1f}s)")
                        
                        # Mark as final chunk if it's the last one
                        if completed_count == len(text_chunks):
                            audio_chunk.is_final = True
                        
                    else:
                        print(f"❌ Failed to generate chunk {chunk_index + 1}")
                        
                except Exception as e:
                    print(f"❌ Error processing chunk {chunk_index + 1}: {e}")
        
        # Sort chunks by their original order
        audio_chunks.sort(key=lambda x: x.chunk_id)
        
        total_time = time.time() - start_time
        print(f"🎤 Streaming TTS complete: {len(audio_chunks)} chunks in {total_time:.1f}s")
        
        return audio_chunks
    
    def _generate_chunk_audio(self, text: str, chunk_id: int, voice: str) -> Optional[AudioChunk]:
        """Generate audio for a single text chunk"""
        try:
            # Generate audio using the existing method logic
            audio_data = self.kokoro.create(text, voice=voice, speed=self.tts_speed, lang="en-us")
            
            # Handle audio data format (same logic as existing method)
            import numpy as np
            
            if isinstance(audio_data, (tuple, list)):
                if len(audio_data) == 2:
                    first_elem, second_elem = audio_data
                    if isinstance(first_elem, np.ndarray) or hasattr(first_elem, '__array__'):
                        audio_data = first_elem
                    elif isinstance(second_elem, np.ndarray) or hasattr(second_elem, '__array__'):
                        audio_data = second_elem
                    else:
                        audio_data = np.array(first_elem, dtype=np.float32)
                elif len(audio_data) == 1:
                    audio_data = audio_data[0]
                else:
                    # Find audio candidate
                    audio_candidate = None
                    for elem in audio_data:
                        if isinstance(elem, np.ndarray) and elem.size > 100:
                            audio_candidate = elem
                            break
                    audio_data = audio_candidate if audio_candidate is not None else audio_data[0]
            
            # Convert to numpy array
            if not isinstance(audio_data, np.ndarray):
                audio_data = np.array(audio_data, dtype=np.float32)
            
            # Handle multi-dimensional arrays
            if audio_data.ndim > 1:
                if audio_data.shape[1] == 1:
                    audio_data = audio_data.flatten()
                elif audio_data.shape[0] == 1:
                    audio_data = audio_data[0]
                else:
                    audio_data = audio_data[:, 0]
            
            # Ensure proper format
            audio_data = np.asarray(audio_data, dtype=np.float32)
            
            # Normalize if needed
            max_val = np.max(np.abs(audio_data))
            if max_val > 1.0:
                audio_data = audio_data / max_val
            
            # Validate
            if len(audio_data) == 0:
                raise ValueError("Empty audio data")
            if np.any(np.isnan(audio_data)) or np.any(np.isinf(audio_data)):
                raise ValueError("Invalid audio data")
            
            # Save chunk audio file
            timestamp = int(time.time() * 1000)  # Use milliseconds for uniqueness
            filename = f"chunk_{self.conversation_id}_{chunk_id}_{timestamp}.wav"
            filepath = os.path.join(self.temp_dir, filename)
            
            sf.write(filepath, audio_data, 24000, format="WAV")
            
            # Calculate duration
            duration = len(audio_data) / 24000.0
            
            return AudioChunk(
                chunk_id=chunk_id,
                text=text,
                audio_file=filepath,
                duration=duration
            )
            
        except Exception as e:
            print(f"❌ Chunk {chunk_id} TTS failed: {e}")
            return None
    
    def generate_tts_audio(self, text: str, voice: str = None) -> Optional[str]:
        """Generate TTS audio for given text"""
        if voice is None:
            voice = self.tts_voice
            
        # Clean the text for TTS (remove markdown formatting)
        clean_text = self.clean_text_for_tts(text)
        print(f"🎤 TTS Text (cleaned): {clean_text[:100]}{'...' if len(clean_text) > 100 else ''}")
            
        try:
            # First try direct API
            try:
                # Generate audio using direct API with cleaned text
                audio_data = self.kokoro.create(clean_text, voice=voice, speed=self.tts_speed, lang="en-us")
                
                # Debug: Print original data info
                print(f"🔧 Direct API: Generated audio data type: {type(audio_data)}, shape: {getattr(audio_data, 'shape', 'no shape')}")
                
                # Handle different audio data types and shapes
                import numpy as np
                
                # Debug: Print original data info
                print(f"🔧 Direct API: Raw data type: {type(audio_data)}")
                if hasattr(audio_data, 'shape'):
                    print(f"🔧 Direct API: Shape: {audio_data.shape}")
                elif isinstance(audio_data, (tuple, list)):
                    print(f"🔧 Direct API: Container length: {len(audio_data)}, item types: {[type(x) for x in audio_data[:3]]}")
                
                # Handle tuple/list return from Kokoro
                if isinstance(audio_data, (tuple, list)):
                    print(f"🔧 Direct API: Tuple/list detected with {len(audio_data)} elements")
                    
                    # Try different tuple unpacking strategies
                    if len(audio_data) == 2:
                        # Common case: (audio_array, sample_rate) or (audio_array, metadata)
                        first_elem, second_elem = audio_data
                        print(f"🔧 Direct API: First element type: {type(first_elem)}, Second: {type(second_elem)}")
                        
                        # Choose the audio data (usually the first element, or the numpy array)
                        if isinstance(first_elem, np.ndarray) or hasattr(first_elem, '__array__'):
                            audio_data = first_elem
                            print("🔧 Direct API: Using first element as audio data")
                        elif isinstance(second_elem, np.ndarray) or hasattr(second_elem, '__array__'):
                            audio_data = second_elem
                            print("🔧 Direct API: Using second element as audio data")
                        else:
                            # Try converting first element
                            try:
                                audio_data = np.array(first_elem, dtype=np.float32)
                                print("🔧 Direct API: Converted first element to numpy array")
                            except Exception as e:
                                print(f"🔧 Direct API: Failed to convert first element: {e}")
                                raise ValueError(f"Cannot extract audio data from tuple: {[type(x) for x in audio_data]}")
                    
                    elif len(audio_data) == 1:
                        # Single element tuple
                        audio_data = audio_data[0]
                        print(f"🔧 Direct API: Extracted single element: {type(audio_data)}")
                    
                    else:
                        # Multiple elements, try to find the audio data
                        print(f"🔧 Direct API: Complex tuple with {len(audio_data)} elements")
                        audio_candidate = None
                        for i, elem in enumerate(audio_data):
                            if isinstance(elem, np.ndarray) and elem.size > 1000:  # Likely audio data
                                audio_candidate = elem
                                print(f"🔧 Direct API: Found audio candidate at index {i}: shape {elem.shape}")
                                break
                        
                        if audio_candidate is not None:
                            audio_data = audio_candidate
                        else:
                            # Fallback to first element
                            audio_data = audio_data[0]
                            print("🔧 Direct API: No clear audio candidate, using first element")
                
                print(f"🔧 Direct API: After tuple processing - type: {type(audio_data)}, shape: {getattr(audio_data, 'shape', 'no shape')}")
                
                # Convert to numpy array if needed
                if not isinstance(audio_data, np.ndarray):
                    audio_data = np.array(audio_data, dtype=np.float32)
                    print(f"🔧 Direct API: Converted to numpy, shape: {audio_data.shape}")
                
                # Handle different array shapes
                if audio_data.ndim > 1:
                    print(f"🔧 Direct API: Multi-dimensional audio detected: {audio_data.shape}")
                    # If multi-channel, take first channel or flatten
                    if audio_data.shape[1] == 1:
                        audio_data = audio_data.flatten()
                        print(f"🔧 Direct API: Flattened single channel: {audio_data.shape}")
                    elif audio_data.shape[0] == 1:
                        audio_data = audio_data[0]
                        print(f"🔧 Direct API: Took first row: {audio_data.shape}")
                    else:
                        # Take the first channel if stereo/multi-channel
                        audio_data = audio_data[:, 0]
                        print(f"🔧 Direct API: Took first channel: {audio_data.shape}")
                
                # Ensure it's float32 and properly shaped
                audio_data = np.asarray(audio_data, dtype=np.float32)
                print(f"🔧 Direct API: Final audio shape: {audio_data.shape}, dtype: {audio_data.dtype}")
                
                # Normalize if needed (values should be between -1 and 1)
                max_val = np.max(np.abs(audio_data))
                if max_val > 1.0:
                    audio_data = audio_data / max_val
                    print(f"🔧 Direct API: Normalized audio (max was {max_val:.3f})")
                
                # Validate audio data
                if len(audio_data) == 0:
                    raise ValueError("Empty audio data generated")
                if np.any(np.isnan(audio_data)) or np.any(np.isinf(audio_data)):
                    raise ValueError("Invalid audio data (NaN or Inf values)")
                
                # Save audio file
                timestamp = int(time.time())
                filename = f"tts_{self.conversation_id}_{timestamp}.wav"
                filepath = os.path.join(self.temp_dir, filename)
                
                # Use 24kHz sample rate (Kokoro's native sample rate)
                sf.write(filepath, audio_data, 24000, format="WAV")
                print(f"✅ Direct API success: Audio saved to {filename}")
                return filepath
                
            except Exception as direct_error:
                print(f"⚠️  Direct API failed: {direct_error}, falling back to CLI...")
                return self.generate_tts_audio_cli(text, voice)
                
        except Exception as e:
            print(f"❌ TTS generation failed: {e}")
            return None
    
    def generate_tts_audio_cli(self, text: str, voice: str = None) -> Optional[str]:
        """Generate TTS audio using CLI fallback"""
        if voice is None:
            voice = self.tts_voice
            
        # Clean the text for TTS (remove markdown formatting)
        clean_text = self.clean_text_for_tts(text)
        print(f"🎤 TTS CLI Text (cleaned): {clean_text[:100]}{'...' if len(clean_text) > 100 else ''}")
            
        try:
            import subprocess
            import tempfile
            
            # Create temporary files
            timestamp = int(time.time())
            temp_text_file = os.path.join(self.temp_dir, f"input_{timestamp}.txt")
            audio_filename = f"tts_{self.conversation_id}_{timestamp}.wav"
            audio_filepath = os.path.join(self.temp_dir, audio_filename)
            
            # Write cleaned text to temporary file with UTF-8 encoding
            with open(temp_text_file, 'w', encoding='utf-8') as f:
                f.write(clean_text)
            
            # Get Python executable path
            python_exe = os.path.join(os.getcwd(), ".venv", "Scripts", "python.exe")
            
            # Construct command
            cmd = [
                python_exe,
                "kokoro-tts",
                temp_text_file,
                audio_filepath,
                "--voice", voice,
                "--speed", str(self.tts_speed),
                "--lang", "en-us",
                "--format", "wav"
            ]
            
            # Run the command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=os.getcwd()
            )
            
            # Clean up temporary text file
            if os.path.exists(temp_text_file):
                os.remove(temp_text_file)
            
            if result.returncode == 0 and os.path.exists(audio_filepath):
                return audio_filepath
            else:
                print(f"❌ CLI TTS failed: {result.stderr or result.stdout}")
                return None
                
        except Exception as e:
            print(f"❌ CLI TTS generation failed: {e}")
            return None
    
    def play_audio(self, audio_file: str):
        """Play audio file"""
        try:
            if os.path.exists(audio_file):
                audio_data, sample_rate = sf.read(audio_file)
                sd.play(audio_data, sample_rate)
                sd.wait()  # Wait until playback is finished
        except Exception as e:
            print(f"❌ Audio playback failed: {e}")
    
    def add_message(self, role: str, content: str, audio_file: str = None, voice: str = None, audio_chunks: List[str] = None):
        """Add message to conversation history"""
        message = ConversationMessage(
            role=role,
            content=content,
            timestamp=datetime.now(),
            audio_file=audio_file,
            voice=voice,
            audio_chunks=audio_chunks
        )
        self.conversation_history.append(message)
    
    def chat_web(self, user_input: str, context: str = None) -> Dict:
        """Chat function for web interface - generates audio but doesn't play it"""
        print(f"\n👤 You: {user_input}")
        if context:
            print(f"🧠 Context: {context[:100]}{'...' if len(context) > 100 else ''}")
        
        # Add user message to history
        self.add_message("user", user_input)
        
        # Get AI response with context
        print("🤔 AI is thinking...")
        start_time = time.time()
        ai_response = self.get_ai_response(user_input, context)
        ai_time = time.time() - start_time
        
        print(f"🤖 AI ({ai_time:.1f}s): {ai_response}")
        
        # Generate TTS audio (but don't play it)
        print("🎤 Generating speech...")
        start_time = time.time()
        audio_file = self.generate_tts_audio(ai_response)
        tts_time = time.time() - start_time
        
        if audio_file:
            print(f"✅ Speech generated ({tts_time:.1f}s)")
            
            # Add AI message with audio to history
            self.add_message("assistant", ai_response, audio_file, self.tts_voice)
            
            return {
                "success": True,
                "ai_response": ai_response,
                "audio_file": audio_file,
                "ai_time": ai_time,
                "tts_time": tts_time,
                "total_time": ai_time + tts_time
            }
        else:
            # Add AI message without audio
            self.add_message("assistant", ai_response)
            return {
                "success": True,
                "ai_response": ai_response,
                "audio_file": None,
                "ai_time": ai_time,
                "tts_time": 0,
                "total_time": ai_time,
                "error": "TTS generation failed"
            }
    
    def chat_web_streaming(self, user_input: str, context: str = None) -> Dict:
        """
        Chat function with streaming support for web interface.
        Returns immediate response with streaming audio chunks.
        """
        print(f"\n👤 You: {user_input}")
        if context:
            print(f"🧠 Context: {context[:100]}{'...' if len(context) > 100 else ''}")
        
        # Add user message to history
        self.add_message("user", user_input)
        
        # Get AI response with context
        print("🤔 AI is thinking...")
        start_time = time.time()
        ai_response = self.get_ai_response(user_input, context)
        ai_time = time.time() - start_time
        
        print(f"🤖 AI ({ai_time:.1f}s): {ai_response}")
        
        # Generate streaming TTS audio
        print("🎤 Generating streaming speech...")
        tts_start_time = time.time()
        
        try:
            audio_chunks = self.generate_tts_audio_streaming(ai_response)
            
            if audio_chunks:
                # Calculate total TTS time
                tts_time = time.time() - tts_start_time
                
                # Prepare chunk information for frontend
                chunk_info = []
                for chunk in audio_chunks:
                    chunk_info.append({
                        "chunk_id": chunk.chunk_id,
                        "text": chunk.text,
                        "audio_file": os.path.basename(chunk.audio_file),
                        "duration": chunk.duration,
                        "is_final": chunk.is_final
                    })
                
                print(f"✅ Streaming speech generated ({tts_time:.1f}s)")
                
                # Add AI message with streaming audio chunks to history
                chunk_files = [chunk.audio_file for chunk in audio_chunks]
                self.add_message("assistant", ai_response, None, self.tts_voice, chunk_files)
                
                return {
                    "success": True,
                    "ai_response": ai_response,
                    "streaming": True,
                    "audio_chunks": chunk_info,
                    "timing": {
                        "ai_time": ai_time,
                        "tts_time": tts_time,
                        "total_time": ai_time + tts_time,
                        "first_chunk_ready": min([c.duration for c in audio_chunks]) if audio_chunks else tts_time
                    }
                }
            else:
                # Fallback to regular TTS if streaming fails
                print("⚠️ Streaming TTS failed, falling back to regular TTS...")
                return self.chat_web(user_input, context)
                
        except Exception as e:
            print(f"❌ Streaming TTS error: {e}")
            # Fallback to regular TTS
            return self.chat_web(user_input, context)
    
    def chat(self, user_input: str, play_audio: bool = True) -> Dict:
        """Main chat function"""
        print(f"\n👤 You: {user_input}")
        
        # Add user message to history
        self.add_message("user", user_input)
        
        # Get AI response
        print("🤔 AI is thinking...")
        start_time = time.time()
        ai_response = self.get_ai_response(user_input)
        ai_time = time.time() - start_time
        
        print(f"🤖 AI ({ai_time:.1f}s): {ai_response}")
        
        # Generate TTS audio
        if play_audio:
            print("🎤 Generating speech...")
            start_time = time.time()
            audio_file = self.generate_tts_audio(ai_response)
            tts_time = time.time() - start_time
            
            if audio_file:
                print(f"✅ Speech generated ({tts_time:.1f}s)")
                
                # Add AI message with audio to history
                self.add_message("assistant", ai_response, audio_file, self.tts_voice)
                
                # Play audio
                print("🔊 Playing audio...")
                self.play_audio(audio_file)
                
                return {
                    "success": True,
                    "ai_response": ai_response,
                    "audio_file": audio_file,
                    "ai_time": ai_time,
                    "tts_time": tts_time,
                    "total_time": ai_time + tts_time
                }
            else:
                # Add AI message without audio
                self.add_message("assistant", ai_response)
                return {
                    "success": True,
                    "ai_response": ai_response,
                    "audio_file": None,
                    "ai_time": ai_time,
                    "tts_time": 0,
                    "total_time": ai_time,
                    "error": "TTS generation failed"
                }
        else:
            # Add AI message without audio
            self.add_message("assistant", ai_response)
            return {
                "success": True,
                "ai_response": ai_response,
                "audio_file": None,
                "ai_time": ai_time,
                "tts_time": 0,
                "total_time": ai_time
            }
    
    def change_voice(self, voice: str):
        """Change TTS voice"""
        if voice in self.voices:
            self.tts_voice = voice
            print(f"🎤 Voice changed to: {self.voices[voice]}")
        else:
            print(f"❌ Unknown voice: {voice}")
            print("Available voices:")
            for v, desc in self.voices.items():
                print(f"  {v}: {desc}")
    
    def list_voices(self):
        """List available voices"""
        print("\n🎤 Available voices:")
        for voice, description in self.voices.items():
            current = " (current)" if voice == self.tts_voice else ""
            print(f"  {voice}: {description}{current}")
    
    def save_conversation(self, filename: str = None) -> str:
        """Save conversation history to JSON"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}.json"
        
        # Convert messages to dict format
        history_dict = {
            "conversation_id": self.conversation_id,
            "created_at": datetime.now().isoformat(),
            "ollama_model": self.ollama_model,
            "tts_voice": self.tts_voice,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "audio_file": msg.audio_file,
                    "voice": msg.voice
                }
                for msg in self.conversation_history
            ]
        }
        
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(history_dict, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Conversation saved to: {filepath}")
        return filepath
    
    def get_stats(self) -> Dict:
        """Get conversation statistics"""
        total_messages = len(self.conversation_history)
        user_messages = sum(1 for msg in self.conversation_history if msg.role == "user")
        ai_messages = sum(1 for msg in self.conversation_history if msg.role == "assistant")
        
        total_chars = sum(len(msg.content) for msg in self.conversation_history)
        avg_message_length = total_chars / total_messages if total_messages > 0 else 0
        
        return {
            "total_messages": total_messages,
            "user_messages": user_messages,
            "ai_messages": ai_messages,
            "total_characters": total_chars,
            "avg_message_length": round(avg_message_length, 1),
            "conversation_duration": (
                (self.conversation_history[-1].timestamp - self.conversation_history[0].timestamp).total_seconds()
                if total_messages > 0 else 0
            )
        }

def main():
    """Main interactive loop"""
    print("🤖 Kokoro TTS + Ollama Conversational AI")
    print("=" * 50)
    
    # Initialize conversational AI
    try:
        ai = ConversationalAI()
    except Exception as e:
        print(f"❌ Failed to initialize AI system: {e}")
        return
    
    # Test Ollama connection
    if not ai.test_ollama_connection():
        print("❌ Cannot connect to Ollama. Make sure it's running:")
        print("   ollama serve")
        return
    
    print("✅ Connected to Ollama successfully!")
    print("\n💡 Commands:")
    print("  'quit' or 'exit' - End conversation")
    print("  'voice <name>' - Change TTS voice")
    print("  'voices' - List available voices") 
    print("  'stats' - Show conversation statistics")
    print("  'save' - Save conversation")
    print("  'mute' - Toggle audio playback")
    print("")
    
    audio_enabled = True
    
    try:
        while True:
            # Get user input
            user_input = input("\n👤 You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n👋 Goodbye! Saving conversation...")
                ai.save_conversation()
                break
            elif user_input.lower().startswith('voice '):
                voice_name = user_input[6:].strip()
                ai.change_voice(voice_name)
                continue
            elif user_input.lower() == 'voices':
                ai.list_voices()
                continue
            elif user_input.lower() == 'stats':
                stats = ai.get_stats()
                print("\n📊 Conversation Statistics:")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
                continue
            elif user_input.lower() == 'save':
                ai.save_conversation()
                continue
            elif user_input.lower() == 'mute':
                audio_enabled = not audio_enabled
                status = "enabled" if audio_enabled else "disabled"
                print(f"🔊 Audio playback {status}")
                continue
            
            # Process conversation
            result = ai.chat(user_input, play_audio=audio_enabled)
            
            if not result["success"]:
                print("❌ Error in conversation processing")
            else:
                # Show timing information
                timing_info = f"(AI: {result['ai_time']:.1f}s"
                if result.get('tts_time', 0) > 0:
                    timing_info += f", TTS: {result['tts_time']:.1f}s"
                timing_info += f", Total: {result['total_time']:.1f}s)"
                print(f"⏱️ {timing_info}")
                
                if result.get('error'):
                    print(f"⚠️ {result['error']}")
    
    except KeyboardInterrupt:
        print("\n\n👋 Conversation interrupted. Saving...")
        ai.save_conversation()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("💾 Saving conversation before exit...")
        ai.save_conversation()

if __name__ == "__main__":
    main()