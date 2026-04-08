# ai_decisions.py
import os
import json
import random
from typing import Dict, List, Tuple
from openenv.models import Action

# ── Action catalogs (match openenv.yaml exactly) ──────────────────────────────
ACTION_MAP = {
    "ceo": ["expand_market", "reduce_costs", "launch_feature", "do_nothing"],
    "cfo": ["cut_costs", "increase_marketing", "invest_growth", "hold"],
    "cto": ["fix_bugs", "build_feature", "scale_infrastructure", "ignore"],
}

# ── Main entry point used by baseline.py, simulation.py, agents.py ────────────
def ai_choose_action(task: str, state: dict, api_key: str = "") -> Tuple[Action, str]:
    """
    Returns (Action, reason_string).
    Always uses fallback logic.
    """
    from failure_memory import get_recent_failures
    failures = get_recent_failures(task)

    return _fallback_decision(task, state)


# ── Legacy entry point used by agents.py / simulation.py ─────────────────────
def get_ai_decision(role: str, state: dict, failures: List[dict], api_key: str = "") -> str:
    """Returns just the action type string (legacy interface)."""
    action, _ = ai_choose_action(role, state, api_key)
    return action.type


# ── Rule-based fallback ───────────────────────────────────────────────────────
def _fallback_decision(task: str, state: dict) -> Tuple[Action, str]:
    if task == "ceo":
        if state.get("users", 0) < 150:
            return Action(type="expand_market"), "Strategic decision based on state and constraints: users below target, expanding market."
        elif state.get("revenue", 0) < 2500:
            return Action(type="launch_feature"), "Strategic decision based on state and constraints: revenue low, launching features."
        else:
            return Action(type="reduce_costs"), "Strategic decision based on state and constraints: strong position, optimizing costs."

    elif task == "cfo":
        cash = state.get("cash", 5000)
        burn_rate = state.get("burn_rate", 500)
        runway = cash / max(burn_rate, 1)
        if runway < 8:
            return Action(type="cut_costs"), "Strategic decision based on state and constraints: low runway, cutting costs."
        elif state.get("revenue", 0) > state.get("expenses", 0) * 1.4:
            return Action(type="invest_growth"), "Strategic decision based on state and constraints: strong margins, investing in growth."
        else:
            return Action(type="hold"), "Strategic decision based on state and constraints: holding to preserve cash."

    elif task == "cto":
        if state.get("bug_count", 0) > 40:
            return Action(type="fix_bugs"), "Strategic decision based on state and constraints: high bug count, fixing bugs first."
        elif state.get("system_load", 0) > 0.75:
            return Action(type="scale_infrastructure"), "Strategic decision based on state and constraints: overloaded system, scaling infrastructure."
        else:
            return Action(type="build_feature"), "Strategic decision based on state and constraints: stable system, shipping features."

    return Action(type="hold"), "Strategic decision based on state and constraints: maintaining position."


# ── Streamlit-aware wrapper (used when API key is in st.session_state) ─────────
def get_ai_decision_streamlit(role: str, state: dict, failures: list) -> str:
    """For use inside Streamlit context only."""
    try:
        import streamlit as st
        api_key = st.session_state.get("grok_api_key", "")
    except Exception:
        api_key = os.environ.get("GROQ_API_KEY", "")
    return get_ai_decision(role, state, failures, api_key)
