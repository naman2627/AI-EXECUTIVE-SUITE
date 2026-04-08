import os
from pathlib import Path

# Load .env from project root
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass

from groq import Groq


GROQ_MODEL = "llama-3.3-70b-versatile"

def _get_client():
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set")
    return Groq(api_key=api_key)

def call_ai(prompt: str) -> str:
    try:
        client = _get_client()
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Groq error: {str(e)}"

def build_conversation_prompt(history, role, mode):
    recent = history[-6:]
    history_text = "\n".join([f"{m['role']}: {m['content']}" for m in recent])

    return f"""
You are an elite {role} (CEO, CFO, CTO).

Mode: {mode}

Conversation:
{history_text}

Respond clearly and intelligently.
"""