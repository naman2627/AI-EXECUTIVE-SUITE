def grade_ceo(state: dict) -> float:
    revenue = state.get("revenue", 2000)
    users = state.get("users", 100)
    rev_score = min(revenue / 5000, 1.0)
    user_score = min(users / 300, 1.0)
    return round(rev_score * 0.6 + user_score * 0.4, 3)