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


LEADERSHIP_KEYWORDS = {
    "leadership",
    "concern",
    "concerns",
    "risk",
    "risks",
    "attention",
    "focus",
    "worried",
    "problem",
    "problems",
    "issue",
    "issues",
}


CROSS_BOARD_KEYWORDS = {
    "compare",
    "comparison",
    "pipeline with work order",
    "pipeline and work order",
    "sales and operations",
    "sales pipeline with execution",
    "pipeline versus execution",
    "pipeline vs execution",
}


def _contains_any(text: str, keywords: set[str]) -> bool:
    text = text.lower()
    return any(keyword in text for keyword in keywords)


def _is_leadership_question(query: str) -> bool:
    return _contains_any(
        query,
        LEADERSHIP_KEYWORDS,
    )


def _is_cross_board_question(query: str) -> bool:
    return _contains_any(
        query,
        CROSS_BOARD_KEYWORDS,
    )


def build_plan(query: str) -> QueryPlan:
    normalized_query = query.strip()

    intent, confidence = detect_intent(
        normalized_query
    )

    entities = extract_entities(
        normalized_query
    )

    # ---------------------------------------------------------
    # Explicit leadership/risk questions
    # ---------------------------------------------------------

    if _is_leadership_question(
        normalized_query
    ):
        intent = "leadership_update"
        confidence = max(
            confidence,
            0.95,
        )

    # ---------------------------------------------------------
    # Explicit cross-board questions
    # ---------------------------------------------------------

    elif _is_cross_board_question(
        normalized_query
    ):
        intent = "cross_board_analysis"
        confidence = max(
            confidence,
            0.95,
        )

    # ---------------------------------------------------------
    # Unknown question
    # ---------------------------------------------------------

    if intent == "unknown":
        return QueryPlan(
            original_query=normalized_query,
            intent=intent,
            confidence=0.0,
            clarification_required=True,
            clarification_question=(
                "Could you clarify what you want to analyze — "
                "pipeline, revenue, work orders, billing, "
                "collections, sector performance, or "
                "leadership risks?"
            ),
        )

    # ---------------------------------------------------------
    # Metrics
    # ---------------------------------------------------------

    metrics: list[str] = []

    if intent in {
        "pipeline_health",
        "pipeline_value",
    }:
        metrics = [
            "pipeline_value",
            "weighted_pipeline",
            "deal_count",
        ]

    elif intent == "revenue":
        metrics = [
            "billed_value",
            "collected_value",
        ]

    elif intent == "accounts_receivable":
        metrics = [
            "amount_receivable",
        ]

    elif intent == "billing":
        metrics = [
            "billed_value",
            "amount_to_be_billed",
        ]

    elif intent == "collections":
        metrics = [
            "collected_value",
            "amount_receivable",
        ]

    elif intent in {
        "sector_performance",
        "cross_board_analysis",
        "leadership_update",
    }:
        metrics = [
            "deal_count",
            "pipeline_value",
            "weighted_pipeline",
            "work_order_count",
            "billed_value",
            "collected_value",
            "amount_to_be_billed",
            "amount_receivable",
        ]

    elif intent in {
        "work_order_performance",
        "operational_status",
        "execution_performance",
    }:
        metrics = [
            "work_order_count",
            "billed_value",
            "collected_value",
        ]

    # ---------------------------------------------------------
    # Grouping
    # ---------------------------------------------------------

    group_by: list[str] = []

    query_lower = normalized_query.lower()

    if (
        "sector" in entities
        or "sectors" in query_lower
        or "by sector" in query_lower
    ):
        group_by.append("sector")

    if "owner" in query_lower:
        group_by.append("owner_code")

    if (
        "stage" in query_lower
        or "by stage" in query_lower
    ):
        group_by.append("deal_stage")

    return QueryPlan(
        original_query=normalized_query,
        intent=intent,
        datasets=INTENT_DATASETS.get(
            intent,
            [],
        ),
        filters=entities,
        metrics=metrics,
        group_by=group_by,
        confidence=confidence,
        limit=10 if group_by else None,
    )