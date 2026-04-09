def grade_cto(state: dict) -> float:
    feature_backlog = state.get("feature_backlog", 20)
    infra_score = state.get("infra_score", 0.5)
    # Smaller backlog = better score, but never fully 0 or 1
    backlog_score = max(0.0, 1.0 - feature_backlog / 50.0)
    raw = backlog_score * 0.6 + min(infra_score, 1.0) * 0.4
    # Strictly between 0 and 1 (open interval)
    return round(max(0.01, min(0.99, raw)), 3)
