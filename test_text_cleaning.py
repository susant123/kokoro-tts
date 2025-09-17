#!/usr/bin/env python3
"""
Test script to demonstrate the text cleaning functionality for TTS
"""

import re

def clean_text_for_tts(text: str) -> str:
    """Clean text by removing markdown formatting characters for TTS"""
    
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

if __name__ == "__main__":
    # Test cases with various markdown formatting
    test_cases = [
        "## Chapter 1: Introduction\n\nThis is **bold text** and *italic text*.",
        
        "Here are the key points:\n\n1. First point\n2. Second point\n- Bullet item\n- Another bullet",
        
        "Use `this.method()` for implementation.\n\n```python\nprint('code block')\n```",
        
        "> This is a blockquote\n\n**Important**: Check the *documentation* for details.",
        
        "### Advanced Features\n\n1. **Performance**: Very fast\n2. **Usability**: Easy to use\n\n> Remember to test your code!"
    ]
    
    print("🧪 Testing Text Cleaning for TTS")
    print("=" * 50)
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}:")
        print("Original:")
        print(f'"{test_text}"')
        
        cleaned = clean_text_for_tts(test_text)
        print("Cleaned for TTS:")
        print(f'"{cleaned}"')
        print("-" * 30)
    
    print("\n✅ Text cleaning demonstration complete!")
    print("The TTS system will now receive clean text without markdown formatting.")