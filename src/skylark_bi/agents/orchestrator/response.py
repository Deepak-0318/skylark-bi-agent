def format_answer(plan, result):
    if not result.metrics and result.caveats:
        return "I couldn't find enough usable data to answer this query."

    if plan.intent == "leadership_update":
        return _leadership(result)

    parts = []

    for key, value in result.metrics.items():
        if value is None:
            continue

        if isinstance(value, float):
            parts.append(f"{key.replace('_', ' ').title()}: {value:,.2f}")
        else:
            parts.append(f"{key.replace('_', ' ').title()}: {value}")

    return "\n".join(parts) or "No usable metrics were found."


def _leadership(result):
    lines = ["Leadership Summary"]

    for key, value in result.metrics.items():
        if value is not None:
            lines.append(
                f"- {key.replace('_', ' ').title()}: {value:,.2f}"
                if isinstance(value, float)
                else f"- {key.replace('_', ' ').title()}: {value}"
            )

    if result.insights:
        lines.append("\nKey insights:")
        lines.extend(f"- {x}" for x in result.insights)

    if result.risks:
        lines.append("\nRisks:")
        lines.extend(f"- {x}" for x in result.risks)

    return "\n".join(lines)