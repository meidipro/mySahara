"""
Test Groq API specifically to verify it's working.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

groq_key = os.getenv("GROQ_API_KEY")

print("=" * 60)
print("Testing Groq API Specifically")
print("=" * 60)

if not groq_key:
    print("[ERROR] GROQ_API_KEY not found")
    sys.exit(1)

print(f"\nGROQ_API_KEY found: Yes")
print(f"Key (first 20 chars): {groq_key[:20]}...")

try:
    from groq import Groq

    client = Groq(api_key=groq_key)

    print("\nTesting different Groq models:")
    print("-" * 60)

    # Test model 1: llama-3.3-70b-versatile
    print("\n1. Testing: llama-3.3-70b-versatile")
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful medical assistant."},
                {"role": "user", "content": "Say hello in one sentence."}
            ],
            max_tokens=50,
            temperature=0.7
        )
        print(f"   [OK] Model working!")
        print(f"   Response: {response.choices[0].message.content}")
        print(f"   Tokens used: {response.usage.total_tokens}")
    except Exception as e:
        print(f"   [ERROR] {str(e)}")

    # Test model 2: llama-3.3-8b-instant (used in ai_service.py default)
    print("\n2. Testing: llama-3.3-8b-instant")
    try:
        response = client.chat.completions.create(
            model="llama-3.3-8b-instant",
            messages=[
                {"role": "system", "content": "You are a helpful medical assistant."},
                {"role": "user", "content": "What is diabetes? Answer in 2 sentences."}
            ],
            max_tokens=100,
            temperature=0.7
        )
        print(f"   [OK] Model working!")
        print(f"   Response: {response.choices[0].message.content}")
        print(f"   Tokens used: {response.usage.total_tokens}")
    except Exception as e:
        print(f"   [ERROR] {str(e)}")

    # Test model 3: Test with medical query
    print("\n3. Testing medical query with llama-3.3-70b-versatile:")
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful medical health assistant for mySahara Health App."},
                {"role": "user", "content": "What are common symptoms of high blood pressure?"}
            ],
            max_tokens=200,
            temperature=0.7
        )
        print(f"   [OK] Medical query working!")
        print(f"   Response: {response.choices[0].message.content}")
        print(f"   Tokens used: {response.usage.total_tokens}")
    except Exception as e:
        print(f"   [ERROR] {str(e)}")

except ImportError:
    print("\n[ERROR] Groq package not installed. Run: pip install groq")
except Exception as e:
    print(f"\n[ERROR] Failed to test Groq: {str(e)}")

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)
