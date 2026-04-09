def grade_cfo(state: dict) -> float:
    cash = state.get("cash", 5000)
    burn_rate = state.get("burn_rate", 500)
    revenue = state.get("revenue", 3000)
    expenses = state.get("expenses", 2000)
    runway = cash / max(burn_rate, 1)
    profit_margin = (revenue - expenses) / max(revenue, 1)
    runway_score = min(runway / 12, 1.0)
    profit_score = max(0.0, min(profit_margin, 1.0))
    raw = runway_score * 0.5 + profit_score * 0.5
    # Strictly between 0 and 1 (open interval)
    return round(max(0.01, min(0.99, raw)), 3)
