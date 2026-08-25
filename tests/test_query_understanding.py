from skylark_bi.agents.query_agent import QueryUnderstandingService


VALID_PLAN = {
    "intent": "pipeline_health",
    "datasets": ["deals"],
    "filters": {"sector": "Mining"},
    "date_range": {},
    "metrics": ["pipeline_value", "weighted_pipeline", "deal_count"],
    "group_by": [],
    "sort_by": None,
    "descending": True,
    "limit": None,
    "confidence": 0.95,
    "clarification_required": False,
    "clarification_question": None,
}


class FakeGroqClient:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error

    def generate_query_plan(self, query, allowed_vocabulary):
        if self.error:
            raise self.error
        return self.response


def test_no_api_key_uses_deterministic_fallback(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    plan = QueryUnderstandingService().understand("How is our pipeline looking?")

    assert plan.intent == "pipeline_health"
    assert plan.metrics == ["pipeline_value", "weighted_pipeline", "deal_count"]


def test_valid_groq_plan_is_returned():
    plan = QueryUnderstandingService(FakeGroqClient(VALID_PLAN)).understand(
        "How is the mining pipeline looking?"
    )

    assert plan.intent == "pipeline_health"
    assert plan.filters == {"sector": "Mining"}
    assert plan.original_query == "How is the mining pipeline looking?"


def test_invalid_json_response_falls_back():
    client = FakeGroqClient(error=ValueError("invalid JSON"))

    plan = QueryUnderstandingService(client).understand("What is outstanding in receivables?")

    assert plan.intent == "accounts_receivable"
    assert plan.metrics == ["amount_receivable"]


def test_groq_api_failure_falls_back():
    plan = QueryUnderstandingService(
        FakeGroqClient(error=TimeoutError("timed out"))
    ).understand("Which sectors are performing best?")

    assert plan.intent == "sector_performance"


def test_unsupported_llm_metric_is_rejected():
    invalid_plan = {**VALID_PLAN, "metrics": ["invented_metric"]}

    plan = QueryUnderstandingService(FakeGroqClient(invalid_plan)).understand(
        "How is our pipeline looking?"
    )

    assert plan.intent == "pipeline_health"
    assert "invented_metric" not in plan.metrics


def test_unsupported_llm_intent_is_rejected():
    invalid_plan = {**VALID_PLAN, "intent": "calculate_profit"}

    plan = QueryUnderstandingService(FakeGroqClient(invalid_plan)).understand(
        "How is our pipeline looking?"
    )

    assert plan.intent == "pipeline_health"