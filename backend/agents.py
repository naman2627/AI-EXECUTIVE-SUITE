import requests
from openenv.models import Action
from failure_memory import get_recent_failures

# Simulated strategy knowledge base
CEO_STRATEGIES = """
Focus on growth and profitability with basic prioritization:
- expand when users are low
- launch product improvements when momentum slows
"""

CFO_STRATEGIES = """
Focus on cash runway and disciplined spend:
- keep runway healthy
- reduce burn and invest selectively
"""

CTO_STRATEGIES = """
Focus on reliability and scalable delivery:
- fix critical bugs quickly
- scale infrastructure when load is high
"""

api_enabled = True


def ai_choose_action(task: str, state: dict):
    try:
        if task == "ceo":
            strategy_text = CEO_STRATEGIES
            action_list = "expand_market, reduce_costs, launch_feature, do_nothing"
            state_block = f"""
Current state:
Revenue: {state['revenue']}
Users: {state['users']}
Market Growth: {state['market_growth']}
Competitor Pressure: {state['competitor_pressure']}
"""

        elif task == "cfo":
            strategy_text = CFO_STRATEGIES
            action_list = "cut_costs, increase_marketing, invest_growth, hold"
            state_block = f"""
Current state:
Cash: {state['cash']}
Burn Rate: {state['burn_rate']}
Expenses: {state['expenses']}
Revenue: {state['revenue']}
"""

        elif task == "cto":
            strategy_text = CTO_STRATEGIES
            action_list = "build_feature, scale_infrastructure, ignore"
            state_block = f"""
Current state:
Feature Backlog: {state.get('feature_backlog', 0)}
"""

        else:
            raise ValueError(f"Unknown task: {task}")

        if not api_enabled:
            fallback = fallback_choose_action(task, state)
            return fallback, "Strategy-based fallback decision"

        recent_failures = get_recent_failures(task)
        failure_text = ""

        if recent_failures:
            failure_text = "Past failures:\n"
            for f in recent_failures:
                failure_text += f"- {f['action']} failed: {f['issue']}\n"

        user_prompt = f"""
You are an expert {task.upper()} strategist.

Think carefully before acting.

State:
{state_block}

{failure_text}

Choose ONE action from:
{action_list}

Rules:

* Avoid repeating past failures
* Think about long-term impact
* Be practical

Respond ONLY in this format:

Action: <action>
Reason: <short strategic reason>
"""

        try:
            res = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": user_prompt,
                    "stream": False
                },
                timeout=30
            )
            response_data = res.json()
            output = response_data.get("response", "")
        except Exception:
            fallback = fallback_choose_action(task, state)
            return fallback, "Fallback: error"

        output_lower = output.lower()

        valid_actions = {
            "ceo": ["expand_market", "reduce_costs", "launch_feature", "do_nothing"],
            "cfo": ["cut_costs", "increase_marketing", "invest_growth", "hold"],
            "cto": ["build_feature", "scale_infrastructure", "ignore"]
        }

        action = None
        for valid in valid_actions[task]:
            if valid in output_lower:
                action = valid
                break

        if "reason:" in output_lower:
            reason = output.split("Reason:", 1)[-1].strip()
        elif "because" in output_lower:
            reason = output.strip()
        else:
            reason = "Strategy-based decision"

        reason = reason + " | Strategic decision based on state and constraints"

        if action in valid_actions[task]:
            return Action(type=action), reason or "Reason not provided"

        fallback = fallback_choose_action(task, state)
        return fallback, "Fallback: invalid AI output"

    except Exception as e:
        print(f"AI decision failed: {e}")
        fallback = fallback_choose_action(task, state)
        return fallback, "Fallback: error"


def fallback_choose_action(task: str, state: dict):
    if task == "ceo":
        if state["users"] < 120:
            return Action(type="expand_market"), "Fallback: expand market to increase users"
        elif state["revenue"] < 1200:
            return Action(type="reduce_costs"), "Fallback: reduce costs to improve efficiency"
        else:
            return Action(type="launch_feature"), "Fallback: launch feature for growth"

    elif task == "cfo":
        cash = state["cash"]
        burn = state["burn_rate"]
        revenue = state["revenue"]
        expenses = state["expenses"]

        profit = revenue - expenses
        runway = cash / max(burn, 1)

        if cash < 1000 or runway < 3:
            return Action(type="cut_costs"), "Fallback: crisis mode - cut costs"

        if profit < 0:
            if burn > 700:
                return Action(type="cut_costs"), "Fallback: negative profit - cut costs"
            else:
                return Action(type="hold"), "Fallback: negative profit - hold"

        if profit > 0 and runway > 12:
            return Action(type="invest_growth"), "Fallback: strong position - invest"

        if profit > 0:
            return Action(type="increase_marketing"), "Fallback: profitable - increase marketing"

        return Action(type="hold"), "Fallback: hold steady"

    elif task == "cto":
        if state.get("feature_backlog", 0) > 10:
            return Action(type="build_feature"), "Fallback: standard conditions - build"
        else:
            return Action(type="scale_infrastructure"), "Fallback: caught up - scale"

    return Action(type="do_nothing"), "Fallback: no action needed"
