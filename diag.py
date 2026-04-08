import os
import sys

# 1. Print python executable path to see if it's the right env
print("Python Executable:", sys.executable)

# 2. Try loading dotenv like backend/main.py
try:
    from dotenv import load_dotenv
    loaded = load_dotenv(os.path.abspath('.env'))
    print("load_dotenv result:", loaded)
except ImportError:
    print("python-dotenv NOT INSTALLED")

# 3. Check what chat.py sees
import chat
print("chat.py GROQ_AVAILABLE:", chat.GROQ_AVAILABLE)
print("chat.py GROQ_API_KEY via _get_api_key():", repr(chat._get_api_key()))
print("os.environ['GROQ_API_KEY']:", repr(os.environ.get("GROQ_API_KEY", "")))

# 4. Do a raw file check to see if .env is real
with open(".env", "r") as f:
    print("\nRAW .ENV FILE CONTENTS:")
    print(repr(f.read()))

