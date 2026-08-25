# Skylark Drones — Decision Log

## 1. Architecture

The system is divided into specialized capabilities:

- Monday Integration Agent
- Data Resilience Agent
- Query Understanding Agent
- Business Intelligence Agent
- Final Orchestrator

The separation allows deterministic analytics to remain independent from
LLM-based interpretation and response generation.

## 2. Data Source

The supplied CSV exports are used only for development and dataset
understanding.

The production agent will query Monday.com dynamically and will not hardcode
the supplied business data.

## 3. Missing Data

Missing values are not automatically imputed unless there is a defensible
business rule.

The agent should explicitly communicate important data-quality limitations.

## 4. Closure Probability

The Closure Probability field contains qualitative values:

- High
- Medium
- Low

No numerical probability mapping is assumed because the dataset does not
provide an explicit mapping.

## 5. Cross-board Relationships

Deal Name ↔ Deal name masked is treated as a candidate record-level
relationship because normalized values show strong overlap.

Owner code ↔ BD/KAM Personnel code is treated as a shared owner dimension.

Sector/service ↔ Sector is treated as a shared analytical dimension.

Client Code ↔ Customer Name Code is explicitly not used as a join because
the supplied datasets have no observed normalized overlap.

## 6. Duplicate Records

Duplicate Deals are flagged rather than blindly deleted.

A repeated Deal Name is not automatically considered a duplicate because
multiple business records may legitimately share a name.

## 7. Financial Values

Financial fields are masked/anonymized in the supplied data. The system can
perform aggregation and comparison on the supplied values but should not
claim that they represent identifiable real-world monetary amounts.

## 8. Leadership Updates

"Leadership updates" is interpreted as concise executive summaries containing:

- Key metrics
- Major trends
- Risks
- Data-quality caveats
- Important changes
- Recommended areas of attention

The output should prioritize business implications over raw rows.

## 9. What Would Be Improved With More Time

With additional time:

- Establish stronger entity resolution between boards.
- Add historical trend analysis.
- Add automated anomaly detection.
- Add configurable business definitions for metrics.
- Add richer visualization.
- Add caching and observability around Monday API calls.
- Add evaluation datasets for agent accuracy.