import asyncio
import os
from app.core.config import settings
import google.generativeai as genai

async def list_models():
    print(f"Listing models for key ending in ...{settings.GEMINI_API_KEY[-4:]}")
    genai.configure(api_key=settings.GEMINI_API_KEY)
    
    try:
        print("Available models:")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f" - {m.name}")
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    asyncio.run(list_models())
