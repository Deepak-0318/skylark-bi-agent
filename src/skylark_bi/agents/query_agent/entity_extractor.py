import re
from datetime import date


SECTORS = {
    "mining",
    "railways",
    "renewables",
    "construction",
    "powerline",
    "others",
    "energy",
}


def extract_entities(query: str) -> dict:
    q = query.lower()

    result = {}

    for sector in SECTORS:
        if sector in q:
            result["sector"] = sector.title()
            break

    for status in ["won", "lost", "ongoing", "completed", "not started"]:
        if status in q:
            result["status"] = status

    quarters = re.findall(r"\bq([1-4])\b", q)
    if quarters:
        result["quarter"] = int(quarters[0])

    if "this quarter" in q:
        result["relative_period"] = "this_quarter"
    elif "last quarter" in q:
        result["relative_period"] = "last_quarter"
    elif "this month" in q:
        result["relative_period"] = "this_month"
    elif "last month" in q:
        result["relative_period"] = "last_month"
    elif "this year" in q:
        result["relative_period"] = "this_year"
    elif "last year" in q:
        result["relative_period"] = "last_year"

    owner = re.search(r"\bowner[_\s-]?(\d+)\b", q)
    if owner:
        result["owner_code"] = f"OWNER_{int(owner.group(1)):03d}"

    return result