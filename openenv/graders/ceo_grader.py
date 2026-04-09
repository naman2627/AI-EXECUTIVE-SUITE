def grade_ceo(state: dict) -> float:
    revenue = state.get("revenue", 2000)
    users = state.get("users", 100)
    rev_score = min(revenue / 5000, 1.0)
    user_score = min(users / 300, 1.0)
    raw = rev_score * 0.6 + user_score * 0.4
    # Strictly between 0 and 1 (open interval)
    return round(max(0.01, min(0.99, raw)), 3)
