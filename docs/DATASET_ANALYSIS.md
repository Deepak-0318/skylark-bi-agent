# Phase 1 — Dataset Understanding

## Dataset Summary

| Dataset | Records | Columns |
|---|---:|---:|
| Deals | 346 | 12 |
| Work Orders | 176 | 38 |

## Data Quality Summary

### Deals

- Critical missing fields: 1
- Warning fields: 3
- Completely empty columns: 0
- Rows involved in duplicate groups: 20

### Work Orders

- Critical missing fields: 8
- Warning fields: 9
- Completely empty columns: 4
- Rows involved in duplicate groups: 0

## Cross-Board Relationships

| Deals field | Work Orders field | Overlap | Confidence | Recommendation |
|---|---|---:|---|---|
| Deal Name | Deal name masked | 52 | high | Suitable candidate for cross-board matching. |
| Client Code | Customer Name Code | 0 | none | Do not use as a cross-board join key. |
| Owner code | BD/KAM Personnel code | 6 | high | Suitable candidate for cross-board matching. |
| Sector/service | Sector | 6 | high | Suitable candidate for cross-board matching. |

## Supported BI Metrics

| Metric | Dataset | Reliability |
|---|---|---|
| Deal Count | Deals | high |
| Pipeline Value | Deals | medium |
| Deals by Sector | Deals | high |
| Deals by Stage | Deals | high |
| Work Order Count | Work Orders | high |
| Work Orders by Sector | Work Orders | high |
| Order Value | Work Orders | high |
| Billed Value | Work Orders | medium |
| Collected Amount | Work Orders | medium |
| Amount Receivable | Work Orders | high |
| Execution Status | Work Orders | high |
| Sector Pipeline vs Execution | Cross-board | high |

## Key Phase 1 Findings

1. Deals contain significant missingness in close dates, closure probability and deal value.

2. Work Orders contain several completely empty billing and collection fields.

3. Deal Name and Deal name masked show strong normalized overlap and are a candidate record-level relationship.

4. Owner code and BD/KAM Personnel code show strong overlap.

5. Sector/service and Sector provide a reliable shared analytical dimension.

6. Client Code and Customer Name Code have no observed overlap and should not be used as a direct join.

7. Missing values must be communicated as data-quality caveats rather than inferred without evidence.
