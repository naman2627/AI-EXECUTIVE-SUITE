def grade_cto(state: dict) -> float:
    feature_backlog = state.get("feature_backlog", 20)
    # Give a higher score for a smaller backlog
    score = max(0, 1 - feature_backlog / 50)
    return round(score, 3)