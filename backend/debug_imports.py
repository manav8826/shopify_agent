print("Importing langchain_core...")
try:
    from langchain_core.messages import BaseMessage
    print("langchain_core OK")
except Exception as e:
    print(f"langchain_core FAILED: {e}")

print("Importing langchain_google_genai...")
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    print("langchain_google_genai OK")
except Exception as e:
    print(f"langchain_google_genai FAILED: {e}")

print("Importing langchain_experimental...")
try:
    from langchain_experimental.tools import PythonAstREPLTool
    print("langchain_experimental OK")
except Exception as e:
    print(f"langchain_experimental FAILED: {e}")
