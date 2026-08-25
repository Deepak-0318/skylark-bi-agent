def _fmt(value):
    if value is None:
        return None

    if isinstance(value, float):
        return f"{value:,.2f}"

    return f"{value:,}" if isinstance(value, int) else str(value)


def format_answer(plan, result):
    if not result.metrics and result.caveats:
        return "I couldn't find enough usable data to answer this query."

    if plan.intent == "leadership_update":
        return _leadership(result)

    if plan.intent == "cross_board_analysis":
        return _cross_board(result)

    parts = []

    for key, value in result.metrics.items():
        formatted = _fmt(value)

        if formatted is not None:
            parts.append(
                f"{key.replace('_', ' ').title()}: {formatted}"
            )

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


def _cross_board(result):
    m = result.metrics

    deal_count = m.get("deal_count")
    pipeline = m.get("pipeline_value")
    weighted = m.get("weighted_pipeline")
    work_orders = m.get("work_order_count")
    billed = m.get("billed_value")
    receivable = m.get("amount_receivable")

    lines = ["Sales vs Operations"]

    if deal_count is not None and pipeline is not None:
        lines.append(
            f"- Sales pipeline: {deal_count:,} deals worth "
            f"{_fmt(pipeline)}."
        )

    if weighted is not None and pipeline:
        percentage = weighted / pipeline * 100
        lines.append(
            f"- Weighted pipeline: {_fmt(weighted)} "
            f"({percentage:.1f}% of total pipeline)."
        )

    if work_orders is not None:
        lines.append(
            f"- Operational workload: {work_orders:,} work orders."
        )

    if billed is not None:
        lines.append(
            f"- Billed value: {_fmt(billed)}."
        )

    if receivable is not None:
        lines.append(
            f"- Outstanding receivables: {_fmt(receivable)}."
        )

    lines.append("\nLeadership takeaway:")

    if receivable:
        lines.append(
            "The immediate financial attention area is collections, "
            "while the sales pipeline provides a substantially larger "
            "future opportunity than the current operational workload."
        )
    else:
        lines.append(
            "Sales opportunity and operational execution should be "
            "monitored together to ensure pipeline conversion keeps pace "
            "with delivery capacity."
        )

    if result.insights:
        lines.append("\nKey insights:")
        lines.extend(f"- {x}" for x in result.insights)

    if result.risks:
        lines.append("\nRisks:")
        lines.extend(f"- {x}" for x in result.risks)

    return "\n".join(lines)


def _leadership(result):
    lines = ["Leadership Summary"]

    for key, value in result.metrics.items():
        formatted = _fmt(value)

        if formatted is not None:
            lines.append(
                f"- {key.replace('_', ' ').title()}: {formatted}"
            )

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