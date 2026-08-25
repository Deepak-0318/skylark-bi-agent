"""
Executive response generation.

Groq is used only to turn validated BI results into a concise
founder-level explanation. Business calculations remain deterministic.
"""

from __future__ import annotations

import json
import os
from typing import Any

from .schemas import FinalAnswer


DEFAULT_MODEL = "openai/gpt-oss-20b"


class GroqResponseClient:
    """Generate concise executive responses from validated BI results."""

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
    ) -> None:
        if not api_key:
            raise ValueError("GROQ_API_KEY is not configured.")

        from groq import Groq

        self.client = Groq(api_key=api_key, timeout=30)
        self.model = model

    @classmethod
    def from_environment(cls):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key or api_key == "YOUR_GROQ_API_KEY":
            return None

        return cls(
            api_key=api_key,
            model=os.getenv("GROQ_MODEL", DEFAULT_MODEL),
        )

    def generate(
        self,
        query: str,
        intent: str,
        metrics: dict[str, Any],
        insights: list[str],
        risks: list[str],
        caveats: list[str],
    ) -> str:

        payload = {
            "query": query,
            "intent": intent,
            "metrics": metrics,
            "insights": insights,
            "risks": risks,
            "caveats": caveats,
        }

        prompt = (
            "Write a concise founder-level business intelligence answer.\n\n"
            "Rules:\n"
            "1. Use ONLY the supplied metrics, insights, risks and caveats.\n"
            "2. Never invent or estimate numbers.\n"
            "3. Do not perform new calculations.\n"
            "4. Clearly explain the business implication.\n"
            "5. Mention important risks.\n"
            "6. Mention caveats when present.\n"
            "7. Keep the answer under 180 words.\n"
            "8. Use simple professional language.\n"
            "9. Do not mention Groq, LLMs, agents, prompts or internal systems.\n\n"
            f"Validated BI result:\n{json.dumps(payload, default=str)}"
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a concise founder-level business "
                        "intelligence assistant."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.1,
            max_tokens=300,
        )

        content = response.choices[0].message.content

        if not isinstance(content, str) or not content.strip():
            raise ValueError("Groq returned an empty response.")

        return content.strip()


def _deterministic_answer(plan, result) -> str:
    """Safe fallback when LLM response generation is unavailable."""

    if not result.metrics and result.caveats:
        return "I couldn't find enough usable data to answer this query."

    if plan.intent == "leadership_update":
        return _leadership(result)

    parts = []

    for key, value in result.metrics.items():
        if value is None:
            continue

        label = key.replace("_", " ").title()

        if isinstance(value, float):
            parts.append(f"{label}: {value:,.2f}")
        else:
            parts.append(f"{label}: {value}")

    if result.insights:
        parts.append("\nKey insights:")
        parts.extend(f"- {x}" for x in result.insights)

    if result.risks:
        parts.append("\nRisks:")
        parts.extend(f"- {x}" for x in result.risks)

    if result.caveats:
        parts.append("\nCaveats:")
        parts.extend(f"- {x}" for x in result.caveats)

    return "\n".join(parts) or "No usable metrics were found."


def _leadership(result):
    lines = ["Leadership Summary"]

    for key, value in result.metrics.items():
        if value is not None:
            label = key.replace("_", " ").title()

            if isinstance(value, float):
                lines.append(f"- {label}: {value:,.2f}")
            else:
                lines.append(f"- {label}: {value}")

    if result.insights:
        lines.append("\nKey insights:")
        lines.extend(f"- {x}" for x in result.insights)

    if result.risks:
        lines.append("\nRisks:")
        lines.extend(f"- {x}" for x in result.risks)

    if result.caveats:
        lines.append("\nCaveats:")
        lines.extend(f"- {x}" for x in result.caveats)

    return "\n".join(lines)


def format_answer(plan, result, llm_client=None) -> str:
    """
    Generate an executive answer using Groq when available.

    Deterministic formatting remains the fallback.
    """

    if llm_client is not None:
        try:
            return llm_client.generate(
                query=plan.original_query,
                intent=plan.intent,
                metrics=result.metrics,
                insights=result.insights,
                risks=result.risks,
                caveats=result.caveats,
            )
        except Exception:
            pass

    return _deterministic_answer(plan, result)