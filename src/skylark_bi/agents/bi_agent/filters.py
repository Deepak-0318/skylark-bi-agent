def apply_filters(records, filters: dict):
    result = list(records)

    for field, expected in filters.items():
        if field in {"relative_period", "quarter"}:
            continue

        filtered = []

        for record in result:
            value = record.get(field) if isinstance(record, dict) else getattr(
                record, field, None
            )

            if value is None:
                continue

            if str(value).lower() == str(expected).lower():
                filtered.append(record)

        result = filtered

    return result