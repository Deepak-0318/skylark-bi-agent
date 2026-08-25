from .schemas import QueryPlan


ALLOWED_INTENTS = {
    "pipeline_health",
    "pipeline_value",
    "revenue",
    "sector_performance",
    "deal_analysis",
    "work_order_performance",
    "billing",
    "collections",
    "accounts_receivable",
    "operational_status",
    "execution_performance",
    "cross_board_analysis",
    "leadership_update",
}

ALLOWED_DATASETS = {"deals", "work_orders"}

ALLOWED_METRICS = {
    "deal_count",
    "pipeline_value",
    "weighted_pipeline",
    "work_order_count",
    "billed_value",
    "collected_value",
    "amount_to_be_billed",
    "amount_receivable",
}

ALLOWED_GROUP_BY = {
    "sector",
    "owner_code",
    "deal_stage",
}

ALLOWED_FILTERS = {
    "sector",
    "deal_name",
    "customer_name_code",
    "owner_code",
    "deal_status",
    "execution_status",
    "deal_stage",
    "quarter",
    "relative_period",
}

ALLOWED_DATE_RANGE = {
    "start",
    "end",
    "relative_period",
}

ALLOWED_SORT_FIELDS = ALLOWED_METRICS | ALLOWED_GROUP_BY


def _primitive(value):
    return value is None or isinstance(
        value,
        (str, int, float, bool),
    )


def plan_from_llm(
    raw_plan: dict,
    query: str,
) -> QueryPlan:
    """Validate and convert an untrusted LLM response."""

    if not isinstance(raw_plan, dict):
        raise ValueError(
            "The LLM plan must be a JSON object."
        )

    allowed_fields = {
        "intent",
        "datasets",
        "filters",
        "date_range",
        "metrics",
        "group_by",
        "sort_by",
        "descending",
        "limit",
        "confidence",
        "clarification_required",
        "clarification_question",
    }

    if set(raw_plan) - allowed_fields:
        raise ValueError(
            "The LLM plan contains unsupported fields."
        )

    required_fields = {
        "intent",
        "datasets",
        "filters",
        "metrics",
        "group_by",
        "confidence",
        "clarification_required",
    }

    if not required_fields <= set(raw_plan):
        raise ValueError(
            "The LLM plan is missing required fields."
        )

    intent = raw_plan["intent"]
    datasets = raw_plan["datasets"]
    filters = raw_plan["filters"]
    metrics = raw_plan["metrics"]
    group_by = raw_plan["group_by"]
    confidence = raw_plan["confidence"]

    if intent not in ALLOWED_INTENTS:
        raise ValueError(
            "The LLM plan contains an unsupported intent."
        )

    if (
        not isinstance(datasets, list)
        or not datasets
        or not set(datasets) <= ALLOWED_DATASETS
    ):
        raise ValueError(
            "The LLM plan contains unsupported datasets."
        )

    if (
        not isinstance(metrics, list)
        or not set(metrics) <= ALLOWED_METRICS
    ):
        raise ValueError(
            "The LLM plan contains unsupported metrics."
        )

    if (
        not isinstance(group_by, list)
        or not set(group_by) <= ALLOWED_GROUP_BY
    ):
        raise ValueError(
            "The LLM plan contains unsupported grouping."
        )

    if (
        not isinstance(filters, dict)
        or not set(filters) <= ALLOWED_FILTERS
    ):
        raise ValueError(
            "The LLM plan contains malformed filters."
        )

    if any(
        not _primitive(value)
        and not (
            isinstance(value, list)
            and all(_primitive(item) for item in value)
        )
        for value in filters.values()
    ):
        raise ValueError(
            "The LLM plan contains malformed filter values."
        )

    # LLMs commonly return null when no date range is required.
    date_range = raw_plan.get("date_range")

    if date_range is None:
        date_range = {}

    if (
        not isinstance(date_range, dict)
        or not set(date_range) <= ALLOWED_DATE_RANGE
    ):
        raise ValueError(
            "The LLM plan contains a malformed date range."
        )

    if not all(
        _primitive(value)
        for value in date_range.values()
    ):
        raise ValueError(
            "The LLM plan contains malformed date-range values."
        )

    if (
        isinstance(confidence, bool)
        or not isinstance(confidence, (int, float))
        or not 0 <= confidence <= 1
    ):
        raise ValueError(
            "The LLM plan contains invalid confidence."
        )

    sort_by = raw_plan.get("sort_by")

    if sort_by not in ALLOWED_SORT_FIELDS:
        sort_by = None

    limit = raw_plan.get("limit")

    if (
        limit is not None
        and (
            isinstance(limit, bool)
            or not isinstance(limit, int)
            or not 1 <= limit <= 100
        )
    ):
        raise ValueError(
            "The LLM plan contains an invalid limit."
        )

    clarification_required = raw_plan[
        "clarification_required"
    ]

    if not isinstance(
        clarification_required,
        bool,
    ):
        raise ValueError(
            "The LLM plan contains invalid clarification state."
        )

    clarification_question = raw_plan.get(
        "clarification_question"
    )

    if (
        clarification_question is not None
        and not isinstance(
            clarification_question,
            str,
        )
    ):
        raise ValueError(
            "The LLM plan contains an invalid clarification question."
        )

    # LLMs commonly return null when sorting is not requested.
    descending = raw_plan.get("descending")

    if descending is None:
        descending = True

    if not isinstance(descending, bool):
        raise ValueError(
            "The LLM plan contains invalid sort direction."
        )

    return validate_plan(
        QueryPlan(
            original_query=query,
            intent=intent,
            datasets=datasets,
            filters=filters,
            date_range=date_range,
            metrics=metrics,
            group_by=group_by,
            sort_by=sort_by,
            descending=descending,
            limit=limit,
            confidence=float(confidence),
            clarification_required=clarification_required,
            clarification_question=clarification_question,
        )
    )


def validate_plan(
    plan: QueryPlan,
) -> QueryPlan:
    """Apply final safety checks to a query plan."""

    if not plan.original_query.strip():
        plan.clarification_required = True
        plan.clarification_question = (
            "What business question would you like me to answer?"
        )

    return plan