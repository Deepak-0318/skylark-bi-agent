from .metrics import value, total, numeric_values


def group_by(records, field):
    groups = {}

    for record in records:
        key = value(record, field) or "Unknown"
        groups.setdefault(str(key), []).append(record)

    return groups


def grouped_total(records, group_field, metric_field):
    groups = group_by(records, group_field)

    return [
        {
            "group": key,
            "records": len(items),
            "value": total(items, metric_field),
        }
        for key, items in groups.items()
    ]