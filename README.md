# Skylark BI Agent

AI-powered Business Intelligence Agent for Skylark Drones.

The system is designed to answer founder-level business questions by
integrating with Monday.com boards containing Deals and Work Orders data.

## Current Status

### Phase 1 — Dataset Understanding

**Status: Complete**

Phase 1 establishes the data foundation required for the production agent.

It includes:

- Dataset loading
- Schema profiling
- Missing-data analysis
- Duplicate detection
- Cross-board relationship analysis
- Data normalization utilities
- Canonical business models
- Business metric catalog
- Data dictionary
- Dataset analysis documentation
- Automated tests

## Dataset Summary

| Dataset | Records | Columns |
|---|---:|---:|
| Deals | 346 | 12 |
| Work Orders | 176 | 38 |

## Cross-Board Relationships

| Relationship | Confidence |
|---|---|
| Deal Name ↔ Deal name masked | High |
| Owner code ↔ BD/KAM Personnel code | High |
| Sector/service ↔ Sector | High |
| Client Code ↔ Customer Name Code | None |

Client Code and Customer Name Code are intentionally not treated as
a join because no normalized overlap was found.

## Project Structure

```text
skylark-bi-agent/
├── src/
│   └── skylark_bi/
│       ├── phase1/
│       ├── agents/
│       │   ├── monday_agent/
│       │   ├── resilience_agent/
│       │   ├── query_agent/
│       │   ├── bi_agent/
│       │   └── orchestrator/
│       └── core/
├── data/
│   ├── raw/
│   └── processed/
├── docs/
├── scripts/
├── tests/
├── requirements.txt
├── DECISION_LOG.md
└── README.md