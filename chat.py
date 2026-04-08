# chat.py
import os
from typing import List, Optional
from pathlib import Path

# Auto-load .env from project root — works no matter how the server is launched
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


ROLE_PERSONAS = {
    "CEO": "You are an elite CEO with 20 years scaling startups to billion-dollar companies. Think in markets, growth, and competitive moats.",
    "CFO": "You are a seasoned CFO who has managed finances through recessions and hypergrowth. Think in runway, unit economics, and capital efficiency.",
    "CTO": "You are a world-class CTO who has built systems at scale. Think in technical debt, system reliability, and engineering velocity.",
}

MODE_INSTRUCTIONS = {
    "⚡ Quick": "Be concise. Answer in 2-3 sentences. Be tactical and immediately actionable.",
    "🧠 Strategist": (
        "Structure your response exactly as:\n"
        "PROBLEM DIAGNOSIS: What is really happening (2 sentences)\n"
        "OPTION A: Name — pros, cons\n"
        "OPTION B: Name — pros, cons\n"
        "OPTION C: Name — pros, cons\n"
        "RECOMMENDATION: Pick one and say why\n"
        "FIRST MOVE: The exact first action to take today"
    ),
}

# Default model — free on Groq's free tier
GROQ_MODEL = "llama-3.3-70b-versatile"


def _get_api_key() -> str:
    return os.environ.get("GROQ_API_KEY", "")


def call_ai(prompt: str, model: str = "analysis") -> str:
    """Call Groq LLM. model param ignored — always uses GROQ_MODEL for speed."""
    api_key = _get_api_key()
    if not api_key or not GROQ_AVAILABLE:
        return "⚠️ No API key. Set your GROQ_API_KEY environment variable."
    try:
        client = Groq(api_key=api_key)
        message = client.chat.completions.create(
            model=GROQ_MODEL,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.choices[0].message.content
    except Exception as e:
        return f"AI Error: {str(e)}"


def build_conversation_prompt(history: list, user_role: str, agent_role: str, mode: str) -> str:
    """Build a full prompt from chat history, roles, and mode."""
    persona = ROLE_PERSONAS.get(agent_role, ROLE_PERSONAS["CEO"])
    
    # Contextualize for the user role
    if user_role and agent_role:
        persona += f"\n\nYou are advising the {user_role}. Tailor your advice specifically to their perspective while maintaining your {agent_role} expertise."

    mode_instruction = MODE_INSTRUCTIONS.get(mode, MODE_INSTRUCTIONS["⚡ Quick"])

    recent = history[-10:]
    context_lines = []
    for m in recent[:-1]:
        r = m.get("role", "user") if isinstance(m, dict) else m[0]
        c = m.get("content", "") if isinstance(m, dict) else m[1]
        context_lines.append(f"{r.upper()}: {c}")

    latest_msg = recent[-1] if recent else {}
    latest = latest_msg.get("content", "") if isinstance(latest_msg, dict) else latest_msg[1]

    context = "\n".join(context_lines)
    if context:
        return f"{persona}\n\n{mode_instruction}\n\nConversation:\n{context}\n\nUser: {latest}"
    return f"{persona}\n\n{mode_instruction}\n\nUser: {latest}"


class ChatManager:
    def __init__(self, api_key: str):
        if not GROQ_AVAILABLE:
            raise ImportError("Install groq: pip install groq")
        self.client = Groq(api_key=api_key)
        self.model = GROQ_MODEL

    def get_response(self, messages: list, context: str = "") -> str:
        """Get AI response. messages is List[Dict] with 'role' and 'content' keys."""
        try:
            groq_messages = []
            for m in messages[-10:]:
                if isinstance(m, dict):
                    role = "user" if m.get("role") == "user" else "assistant"
                    content = m.get("content", "")
                else:
                    role = "user" if m[0] == "user" else "assistant"
                    content = m[1]
                groq_messages.append({"role": role, "content": content})

            # Fix consecutive same-role messages
            fixed = []
            for msg in groq_messages:
                if fixed and fixed[-1]["role"] == msg["role"]:
                    fixed[-1]["content"] += "\n" + msg["content"]
                else:
                    fixed.append(msg)

            if not fixed:
                fixed = [{"role": "user", "content": "Hello"}]

            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=1000,
                messages=fixed,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"

    def get_strategy(self, user_role: str, agent_role: str, problem: str, history: list = None) -> str:
        """Generate a full structured strategy for the given role and problem."""
        
        history_context = ""
        if history:
            history_lines = []
            for m in history[-10:]:
                if isinstance(m, dict):
                    r = "USER" if m.get("role") == "user" else "ASSISTANT"
                    c = m.get("content", "")
                else:
                    r = "USER" if m[0] == "user" else "ASSISTANT"
                    c = m[1]
                history_lines.append(f"{r}: {c}")
            history_context = "\nConversation Context:\n" + "\n".join(history_lines) + "\n\n"

        prompt = f"""You are an elite {agent_role} strategist advising the company's {user_role}.

{history_context}Problem Context: {problem}

Generate a complete strategy:

STEP 1 — CORE PROBLEM
Diagnose the real issue in 3 lines.

STEP 2 — THREE STRATEGIES
Give exactly 3 strategies, each with a name and 2-sentence description.

STEP 3 — COMPARISON
For each strategy: 2 pros, 2 cons, risk level (Low/Medium/High).

STEP 4 — BEST DECISION
Pick ONE and say exactly why.

STEP 5 — EXECUTION PLAN
5 concrete steps to execute the decision.

STEP 6 — RISKS
3 risks to watch for.

Be sharp, realistic, and non-generic."""
        return call_ai(prompt)


def init_chat_manager() -> Optional[ChatManager]:
    api_key = _get_api_key()
    if api_key:
        try:
            return ChatManager(api_key)
        except Exception:
            return None
    return None