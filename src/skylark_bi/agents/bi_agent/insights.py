def generate_sector_insights(grouped):
    if not grouped:
        return []

    usable = [x for x in grouped if x.get("value") is not None]

    if not usable:
        return []

    strongest = max(usable, key=lambda x: x["value"])

    return [
        f"Highest value concentration is in {strongest['group']} "
        f"with {strongest['value']:,.2f}."
    ]


def generate_pipeline_insights(metrics):
    insights = []

    pipeline = metrics.get("pipeline_value")
    weighted = metrics.get("weighted_pipeline")

    if pipeline is not None and weighted is not None and pipeline:
        ratio = weighted / pipeline * 100

        insights.append(
            f"Weighted pipeline represents {ratio:.1f}% "
            "of total identified pipeline value."
        )

    return insights