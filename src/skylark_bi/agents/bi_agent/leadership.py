def leadership_summary(metrics, insights, risks):
    parts = []

    if metrics.get("pipeline_value") is not None:
        parts.append(
            f"Pipeline value: {metrics['pipeline_value']:,.2f}"
        )

    if metrics.get("billed_value") is not None:
        parts.append(
            f"Billed value: {metrics['billed_value']:,.2f}"
        )

    if metrics.get("collected_value") is not None:
        parts.append(
            f"Collected value: {metrics['collected_value']:,.2f}"
        )

    return {
        "headline": " | ".join(parts) or "No usable headline metrics.",
        "insights": insights[:5],
        "risks": risks[:5],
    }