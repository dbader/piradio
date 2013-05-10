def clamp(v, min_value, max_value):
    """Return a value based on `v` that lies within [`min_value`, `max_value`]."""
    return min(max(min_value, v), max_value)
