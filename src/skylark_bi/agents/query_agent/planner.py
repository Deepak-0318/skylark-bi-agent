from .schemas import QueryPlan
from .intent import detect_intent
from .entity_extractor import extract_entities


INTENT_DATASETS = {
    "pipeline_health": ["deals"],
    "pipeline_value": ["deals"],
    "revenue": ["deals", "work_orders"],
    "sector_performance": ["deals", "work_orders"],
    "deal_analysis": ["deals"],
    "work_order_performance": ["work_orders"],
    "billing": ["work_orders"],
    "collections": ["work_orders"],
    "accounts_receivable": ["work_orders"],
    "operational_status": ["work_orders"],
    "execution_performance": ["work_orders"],
    "cross_board_analysis": ["deals", "work_orders"],
    "leadership_update": ["deals", "work_orders"],
}


def build_plan(query: str) -> QueryPlan:
    intent, confidence = detect_intent(query)
    entities = extract_entities(query)

    if intent == "unknown":
        return QueryPlan(
            original_query=query,
            intent=intent,
            confidence=0.0,
            clarification_required=True,
            clarification_question=(
                "Could you clarify what you want to analyze — "
                "pipeline, revenue, work orders, billing, collections, "
                "or sector performance?"
            ),
        )

    metrics = []

    if intent in {"pipeline_health", "pipeline_value"}:
        metrics = ["pipeline_value", "weighted_pipeline", "deal_count"]

    elif intent == "revenue":
        metrics = ["billed_value", "collected_value"]

    elif intent == "accounts_receivable":
        metrics = ["amount_receivable"]

    elif intent == "billing":
        metrics = ["billed_value", "amount_to_be_billed"]

    elif intent == "collections":
        metrics = ["collected_value", "amount_receivable"]

    elif intent in {
        "sector_performance",
        "cross_board_analysis",
        "leadership_update",
    }:
        metrics = [
            "deal_count",
            "pipeline_value",
            "weighted_pipeline",
            "billed_value",
            "collected_value",
        ]

    elif intent in {
        "work_order_performance",
        "operational_status",
        "execution_performance",
    }:
        metrics = ["work_order_count", "billed_value", "collected_value"]

    group_by = []

    if "sector" in entities or "sectors" in query.lower():
        group_by.append("sector")

    if "owner" in query.lower():
        group_by.append("owner_code")

    if "stage" in query.lower():
        group_by.append("deal_stage")

    return QueryPlan(
        original_query=query,
        intent=intent,
        datasets=INTENT_DATASETS.get(intent, []),
        filters=entities,
        metrics=metrics,
        group_by=group_by,
        confidence=confidence,
        limit=10 if group_by else None,
    )