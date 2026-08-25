"""Small, data-free client for Groq query-plan generation."""

from __future__ import annotations

import json
import os
from typing import Any


DEFAULT_MODEL = "openai/gpt-oss-20b"
DEFAULT_TIMEOUT = 30.0


class GroqQueryClient:
    """Generate structured plans from questions without receiving business data."""

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL, timeout: float = DEFAULT_TIMEOUT):
        if not api_key:
            raise ValueError("GROQ_API_KEY is not configured.")

        try:
            from groq import Groq
        except ImportError as exc:
            raise RuntimeError(
                "The Groq SDK is required for LLM query understanding."
            ) from exc

        self._client = Groq(api_key=api_key, timeout=timeout)
        self.model = model

    @classmethod
    def from_environment(cls) -> "GroqQueryClient | None":
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "YOUR_GROQ_API_KEY":
            return None

        return cls(
            api_key=api_key,
            model=os.getenv("GROQ_MODEL", DEFAULT_MODEL),
            timeout=float(os.getenv("GROQ_TIMEOUT", str(DEFAULT_TIMEOUT))),
        )

    def generate_query_plan(
        self,
        query: str,
        allowed_vocabulary: dict[str, list[str]],
    ) -> dict[str, Any]:
        prompt = (
            "Convert the user's business question into a JSON query plan. "
    "Return JSON only. Never answer the question. "
    "Never invent business data.\n\n"

    "STRICT RULES:\n"
    "1. Use only values from the allowed vocabulary for intent, datasets, "
    "metrics, and group_by.\n"
    "2. filters MUST be a JSON object with string keys and primitive values only.\n"
    "3. If there are no filters, return {}.\n"
    "4. date_range MUST be {} when no date filter is present. Never return null.\n"
    "5. descending MUST be true or false. Never return null.\n"
    "6. If the question compares sales/pipeline with work-order/operations/"
    "execution/billing/collections, use intent='cross_board_analysis' "
    "and include both 'deals' and 'work_orders'.\n"
    "7. For leadership or complete business updates involving both sales and "
    "operations, include both datasets.\n"
    "8. Do not put arbitrary objects inside filters.\n"
    "9. clarification_required must be true only when the question genuinely "
    "cannot be answered from the available vocabulary.\n\n"

    f"Allowed vocabulary:\n"
    f"{json.dumps(allowed_vocabulary, sort_keys=True)}\n\n"

    "Required JSON fields:\n"
    "intent, datasets, filters, date_range, metrics, group_by, "
    "sort_by, descending, limit, confidence, "
    "clarification_required, clarification_question\n\n"

    f"User question:\n{query}"
)
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a query planner for a deterministic BI system.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        if not isinstance(content, str):
            raise ValueError("Groq returned an empty query plan.")
        return json.loads(content)