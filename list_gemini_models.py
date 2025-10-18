"""
List available Gemini models.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

gemini_key = os.getenv("GEMINI_API_KEY")

if gemini_key:
    genai.configure(api_key=gemini_key)

    print("Available Gemini models:")
    print("=" * 60)

    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"Model: {model.name}")
            print(f"  Display Name: {model.display_name}")
            print(f"  Description: {model.description}")
            print()
else:
    print("GEMINI_API_KEY not found")
