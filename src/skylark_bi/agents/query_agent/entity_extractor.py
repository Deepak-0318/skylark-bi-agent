import re


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
    q = query.lower().strip()
    result: dict = {}

    # ---------------------------------------------------------
    # Sector
    # ---------------------------------------------------------

    for sector in SECTORS:
        if re.search(rf"\b{re.escape(sector)}\b", q):
            result["sector"] = sector.title()
            break

    # ---------------------------------------------------------
    # Status
    # ---------------------------------------------------------

    for status in [
        "won",
        "lost",
        "ongoing",
        "completed",
        "not started",
    ]:
        if status in q:
            result["status"] = status
            break

    # ---------------------------------------------------------
    # Quarter
    # ---------------------------------------------------------

    quarters = re.findall(r"\bq([1-4])\b", q)

    if quarters:
        result["quarter"] = int(quarters[0])

    # ---------------------------------------------------------
    # Relative periods
    # ---------------------------------------------------------

    relative_periods = {
        "this quarter": "this_quarter",
        "last quarter": "last_quarter",
        "this month": "this_month",
        "last month": "last_month",
        "this year": "this_year",
        "last year": "last_year",
    }

    for phrase, value in relative_periods.items():
        if phrase in q:
            result["relative_period"] = value
            break

    # ---------------------------------------------------------
    # Owner
    # ---------------------------------------------------------

    owner = re.search(
        r"\bowner[_\s-]?(\d+)\b",
        q,
    )

    if owner:
        result["owner_code"] = (
            f"OWNER_{int(owner.group(1)):03d}"
        )

    return result