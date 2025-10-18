"""
Test script to verify Groq and Gemini API keys are working.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

print("=" * 60)
print("Testing AI API Keys")
print("=" * 60)

# Check if keys exist
groq_key = os.getenv("GROQ_API_KEY")
gemini_key = os.getenv("GEMINI_API_KEY")

print(f"\nGROQ_API_KEY found: {bool(groq_key)}")
if groq_key:
    print(f"GROQ_API_KEY (first 20 chars): {groq_key[:20]}...")

print(f"\nGEMINI_API_KEY found: {bool(gemini_key)}")
if gemini_key:
    print(f"GEMINI_API_KEY (first 20 chars): {gemini_key[:20]}...")

# Test Groq API
print("\n" + "=" * 60)
print("Testing Groq API")
print("=" * 60)

if groq_key:
    try:
        from groq import Groq
        client = Groq(api_key=groq_key)

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello in one word."}
            ],
            max_tokens=10
        )

        print(f"[OK] Groq API working!")
        print(f"Response: {response.choices[0].message.content}")

    except Exception as e:
        print(f"[ERROR] Groq API failed: {str(e)}")
else:
    print("[ERROR] GROQ_API_KEY not found")

# Test Gemini API
print("\n" + "=" * 60)
print("Testing Gemini API")
print("=" * 60)

if gemini_key:
    try:
        import google.generativeai as genai

        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-2.0-flash-001')

        response = model.generate_content("Say hello in one word.")

        print(f"[OK] Gemini API working!")
        print(f"Response: {response.text}")

    except Exception as e:
        print(f"[ERROR] Gemini API failed: {str(e)}")
else:
    print("[ERROR] GEMINI_API_KEY not found")

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)
