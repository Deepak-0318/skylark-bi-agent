from .planner import build_plan
from .groq_client import GroqQueryClient
from .validation import (
    ALLOWED_DATASETS,
    ALLOWED_FILTERS,
    ALLOWED_GROUP_BY,
    ALLOWED_INTENTS,
    ALLOWED_METRICS,
    plan_from_llm,
    validate_plan,
)


class QueryUnderstandingService:
    """Understand business questions using Groq with deterministic fallback."""

    def __init__(self, groq_client=None):
        self.groq_client = groq_client
        self.last_llm_error: str | None = None

        if groq_client is not None:
            return

        try:
            self.groq_client = GroqQueryClient.from_environment()
        except Exception as exc:
            self.groq_client = None
            self.last_llm_error = str(exc)

    def understand(self, query: str):
        """Return a validated query plan."""

        self.last_llm_error = None

        if self.groq_client is not None:
            try:
                raw_plan = self.groq_client.generate_query_plan(
                    query,
                    {
                        "intents": sorted(ALLOWED_INTENTS),
                        "datasets": sorted(ALLOWED_DATASETS),
                        "metrics": sorted(ALLOWED_METRICS),
                        "filters": sorted(ALLOWED_FILTERS),
                        "group_by": sorted(ALLOWED_GROUP_BY),
                    },
                )

                return plan_from_llm(
                    raw_plan,
                    query,
                )

            except Exception as exc:
                self.last_llm_error = (
                    f"{type(exc).__name__}: {exc}"
                )

        plan = build_plan(query)
        return validate_plan(plan)