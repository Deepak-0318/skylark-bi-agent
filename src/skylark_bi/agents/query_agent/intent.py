INTENTS = {
    "pipeline_health": [
        "pipeline", "pipeline health", "sales pipeline",
        "funnel", "sales outlook"
    ],
    "pipeline_value": [
        "pipeline value", "pipeline amount", "deal value"
    ],
    "revenue": [
        "revenue", "sales", "billed", "billing"
    ],
    "sector_performance": [
        "sector", "sectors", "industry"
    ],
    "deal_analysis": [
        "deal", "deals", "opportunity", "opportunities"
    ],
    "work_order_performance": [
        "work order", "work orders", "project", "projects"
    ],
    "billing": [
        "billing", "billed", "invoice", "invoiced"
    ],
    "collections": [
        "collection", "collected", "collections"
    ],
    "accounts_receivable": [
        "receivable", "receivables", "outstanding", "ar"
    ],
    "operational_status": [
        "operational", "execution status", "execution"
    ],
    "execution_performance": [
        "execution performance", "execution", "ongoing", "completed"
    ],
    "cross_board_analysis": [
        "compare deals and work orders",
        "cross board",
        "across boards",
        "sales and operations"
    ],
    "leadership_update": [
        "leadership update",
        "leadership", "management update",
        "founder update", "executive update"
    ],
}


def detect_intent(query: str) -> tuple[str, float]:
    q = query.lower()

    scores = {}

    for intent, keywords in INTENTS.items():
        score = sum(1 for keyword in keywords if keyword in q)
        if score:
            scores[intent] = score

    if not scores:
        return "unknown", 0.0

    best = max(scores, key=scores.get)
    confidence = min(1.0, scores[best] / 2)

    return best, confidence