def compare(current, previous):
    if current is None or previous is None:
        return {
            "current": current,
            "previous": previous,
            "absolute_change": None,
            "percentage_change": None,
        }

    change = current - previous

    percentage = None
    if previous != 0:
        percentage = change / previous * 100

    return {
        "current": current,
        "previous": previous,
        "absolute_change": change,
        "percentage_change": percentage,
    }