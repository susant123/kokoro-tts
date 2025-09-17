"""
Kokoro TTS + Ollama Web Interface
Web-based conversational AI with Llama 3.2 and GPU-accelerated TTS
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import json
import uuid
import threading
import time
from datetime import datetime
from conversational_ai import ConversationalAI

app = Flask(__name__)
app.secret_key = 'kokoro-conversational-ai-2025'

# Global AI instance
ai_instance = None
ai_lock = threading.Lock()

def get_ai_instance():
    """Get or initialize the global AI instance"""
    global ai_instance
    
    with ai_lock:
        if ai_instance is None:
            try:
                print("🔄 Initializing Conversational AI...")
                ai_instance = ConversationalAI()
                print("✅ Conversational AI ready!")
            except Exception as e:
                print(f"❌ Failed to initialize AI: {e}")
                raise
        
        return ai_instance

@app.route('/')
def chat_interface():
    """Main chat interface"""
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Chat API endpoint"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        context = data.get('context', '').strip()
        
        if not user_message:
            return jsonify({
                "success": False,
                "error": "Please enter a message"
            })
        
        # Get AI instance
        ai = get_ai_instance()
        
        # Process the conversation with context - generate audio but don't play it
        result = ai.chat_web(user_message, context if context else None)
        
        if result["success"]:
            return jsonify({
                "success": True,
                "ai_response": result["ai_response"],
                "audio_file": os.path.basename(result["audio_file"]) if result.get("audio_file") else None,
                "timing": {
                    "ai_time": result["ai_time"],
                    "tts_time": result.get("tts_time", 0),
                    "total_time": result["total_time"]
                }
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to process conversation"
            })
            
    except Exception as e:
        print(f"Chat API error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/voice', methods=['POST'])
def api_change_voice():
    """Change TTS voice"""
    try:
        data = request.get_json()
        voice = data.get('voice', '').strip()
        
        if not voice:
            return jsonify({
                "success": False,
                "error": "Please specify a voice"
            })
        
        ai = get_ai_instance()
        
        if voice in ai.voices:
            ai.change_voice(voice)
            return jsonify({
                "success": True,
                "message": f"Voice changed to {ai.voices[voice]}",
                "current_voice": voice
            })
        else:
            return jsonify({
                "success": False,
                "error": f"Unknown voice: {voice}",
                "available_voices": list(ai.voices.keys())
            })
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/voices')
def api_get_voices():
    """Get available voices"""
    try:
        ai = get_ai_instance()
        return jsonify({
            "success": True,
            "voices": ai.voices,
            "current_voice": ai.tts_voice
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/history')
def api_get_history():
    """Get conversation history"""
    try:
        ai = get_ai_instance()
        
        history = []
        for msg in ai.conversation_history:
            history.append({
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "audio_file": os.path.basename(msg.audio_file) if msg.audio_file else None,
                "voice": msg.voice
            })
        
        return jsonify({
            "success": True,
            "history": history,
            "stats": ai.get_stats()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/clear')
def api_clear_history():
    """Clear conversation history"""
    try:
        ai = get_ai_instance()
        ai.conversation_history.clear()
        ai.conversation_id = str(uuid.uuid4())
        
        return jsonify({
            "success": True,
            "message": "Conversation history cleared"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/save')
def api_save_conversation():
    """Save conversation to file"""
    try:
        ai = get_ai_instance()
        filepath = ai.save_conversation()
        
        return jsonify({
            "success": True,
            "message": "Conversation saved successfully",
            "file": os.path.basename(filepath)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/status')
def api_status():
    """Get system status"""
    try:
        ai = get_ai_instance()
        ollama_connected = ai.test_ollama_connection()
        
        return jsonify({
            "success": True,
            "ollama_connected": ollama_connected,
            "ollama_model": ai.ollama_model,
            "tts_voice": ai.tts_voice,
            "gpu_enabled": os.getenv("ONNX_PROVIDER") == "CUDAExecutionProvider",
            "conversation_id": ai.conversation_id,
            "message_count": len(ai.conversation_history)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/audio/<filename>')
def serve_audio(filename):
    """Serve audio files"""
    try:
        ai = get_ai_instance()
        filepath = os.path.join(ai.temp_dir, filename)
        
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=False, mimetype='audio/wav')
        else:
            return "Audio file not found", 404
    except Exception as e:
        return f"Error serving audio: {str(e)}", 500

@app.route('/static/<filename>')
def serve_static(filename):
    """Serve static files"""
    try:
        static_dir = os.path.join(os.path.dirname(__file__), 'static')
        filepath = os.path.join(static_dir, filename)
        
        if os.path.exists(filepath):
            if filename.endswith('.wav'):
                return send_file(filepath, as_attachment=False, mimetype='audio/wav')
            else:
                return send_file(filepath, as_attachment=False)
        else:
            return "Static file not found", 404
    except Exception as e:
        return f"Error serving static file: {str(e)}", 500

if __name__ == '__main__':
    print("🤖 Starting Kokoro TTS + Ollama Web Interface...")
    print("📡 Server will be available at: http://localhost:5002")
    print("🧠 AI Model: Llama 3.2")
    print("🎤 TTS: Kokoro with GPU acceleration")
    
    # Initialize AI on startup
    try:
        get_ai_instance()
    except Exception as e:
        print(f"⚠️ Warning: AI initialization failed: {e}")
        print("🔄 Will attempt to initialize on first request")
    
    app.run(debug=True, host='0.0.0.0', port=5002)