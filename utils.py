# utils.py
import streamlit as st
from typing import List

def safe_rerun():
    st.rerun()

def render_step(title: str, content: str):
    if not content.strip():
        return
    st.markdown(f"### {title}")
    st.markdown(content)
    st.markdown("---")

def display_chat_messages(messages: list):
    """Display chat messages — handles both dict and tuple formats."""
    for m in messages:
        if isinstance(m, dict):
            role = m.get("role", "user")
            content = m.get("content", "")
        else:
            role, content = m[0], m[1]
        st.chat_message(role).write(content)

def format_simulation_step(step: int, role: str, action: str, reward: float) -> str:
    return f"Step {step}: {role.upper()} — {action} (Reward: {reward:.3f})"

def get_role_color(role: str) -> str:
    return {"ceo": "🟢", "cfo": "🟡", "cto": "🔵"}.get(role.lower(), "⚪")

def validate_api_key(api_key: str) -> bool:
    return api_key.startswith("gsk_") and len(api_key) > 20


def get_initial_state(role: str) -> dict:
    return {
        "ceo": {"revenue": 2000, "users": 100, "market_share": 0.1},
        "cfo": {"cash": 5000, "burn_rate": 500, "revenue": 3000, "expenses": 2000},
        "cto": {"feature_backlog": 20},
    }.get(role.lower(), {})