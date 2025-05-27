def clamp(min_value: float, max_value: float, value: float) -> float:
    return min(max(min_value, value), max_value)
