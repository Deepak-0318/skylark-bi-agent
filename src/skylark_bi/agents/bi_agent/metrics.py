def value(record, field):
    if isinstance(record, dict):
        return record.get(field)

    return getattr(record, field, None)


def numeric_values(records, field):
    values = []

    for record in records:
        v = value(record, field)

        if isinstance(v, (int, float)):
            values.append(float(v))

    return values


def count(records):
    return len(records)


def total(records, field):
    return sum(numeric_values(records, field))


def average(records, field):
    values = numeric_values(records, field)
    return sum(values) / len(values) if values else None


def percentage(numerator, denominator):
    if not denominator:
        return None

    return numerator / denominator * 100