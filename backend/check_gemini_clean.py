import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=api_key)

print("--- START MODEL LIST ---")
for m in genai.list_models():
    # Print simplified name to avoid wrapping
    print(m.name)
print("--- END MODEL LIST ---")
