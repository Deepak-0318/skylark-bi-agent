# Skylark BI Agent

**Skylark BI Agent — Founder-level business intelligence powered by Monday.com.**

Skylark BI Agent is a read-only Streamlit application that turns natural-language business questions into validated query plans, retrieves live Monday.com data, and returns deterministic founder-level insights.

## Live Prototype

The hosted application is available at:

**https://skylark-bi-agent-01.streamlit.app**

It is hosted on Streamlit and can be tested directly without local setup.

## Problem Statement

Business data stored in Monday.com often requires leadership to inspect multiple boards manually, combine records, and calculate metrics before making decisions. Skylark BI Agent provides a natural-language founder-level BI interface for understanding pipeline, operations, billing, collections, receivables, and related risks.

## Key Features

- Dynamic, read-only Monday.com integration
- Deals and Work Orders board retrieval
- Natural-language query understanding
- Groq LLM-powered query planning
- Deterministic BI calculations
- Cross-board analysis
- Data resilience and validation
- Business insights and risk detection
- Leadership and founder-level summaries
- Streamlit interface

## Architecture

```text
Streamlit UI
    ↓
Orchestrator
    ↓
Query Understanding Agent
    ↓
Groq LLM
    ↓
Validated Query Plan
    ↓
Monday Integration Agent
    ↓
Deals + Work Orders
    ↓
Canonical Deal / WorkOrder models
    ↓
BI Agent
    ↓
Resilience / Validation
    ↓
Executive Response
```

The Groq LLM interprets the user's question and produces a structured query plan only. The plan is validated before use. Business records remain in the application, and business metrics are calculated deterministically from Monday.com data by the BI Agent.

## Agent Components

### Query Agent

Converts natural-language questions into a `QueryPlan` containing intent, datasets, filters, metrics, grouping, confidence, date context, and clarification state. Groq is optional; malformed, unsupported, or unavailable LLM output falls back to deterministic query understanding.

### Monday Agent

Uses the Monday.com API in read-only mode to discover board schemas, retrieve board items, paginate results, map column variations, normalize records, and reconcile data.

### BI Agent

Performs deterministic filtering, metric calculation, aggregation, comparisons, insight generation, and risk detection over canonical `Deal` and `WorkOrder` models.

### Resilience Agent

Profiles and validates incoming data, normalizes values, assesses readiness, identifies quality issues, and provides caveats when incomplete data affects analysis.

### Orchestrator

Coordinates query understanding, data retrieval, canonical model processing, deterministic BI analysis, resilience checks, and executive response formatting.

## Monday.com Integration

The application uses the Monday.com API in read-only mode. It dynamically discovers board schemas and retrieves board items from:

- Deals board
- Work Orders board

**No business dataset is hardcoded into the application.** Board IDs and credentials are supplied through configuration, while the board contents are retrieved at runtime.

## Groq LLM Query Understanding

Groq is used only for natural-language query understanding. It generates a structured JSON query plan containing:

- `intent`
- `datasets`
- `filters`
- `metrics`
- `group_by`
- `confidence`
- clarification state

The response is checked against the existing supported intents, datasets, metrics, filters, and grouping fields. The LLM does not calculate business metrics, invent business results, or receive the complete business dataset. Only the user's question and query-planning vocabulary are sent to Groq.

If Groq is unavailable, times out, is misconfigured, or returns malformed or unsupported output, the existing deterministic query-understanding implementation is used.

## Data Resilience

The application is designed to handle:

- Missing and null values
- Inconsistent dates
- Numeric parsing issues
- Monday.com column-name variations
- Malformed LLM plans
- Incomplete source data

Validation and readiness checks preserve usable records where possible and surface caveats when data quality limits an answer.

## Business Intelligence

Supported analytical areas include:

- Pipeline health
- Pipeline value
- Weighted pipeline
- Sector performance
- Revenue and billing
- Collections
- Outstanding receivables
- Work-order performance
- Operational status
- Cross-board analysis
- Leadership updates

## Example Questions

- How is our pipeline looking?
- How is the mining sector pipeline?
- What is our outstanding receivable?
- Compare our sales pipeline with work order execution.
- Where should leadership focus?
- Give me a complete update on Sakura.

## Leadership Update Interpretation

A leadership update combines the available signals into an executive summary covering:

- Pipeline health
- Weighted pipeline
- Operational workload
- Billing and collection position
- Receivables
- Risks
- Important insights

## Project Structure

```text
app.py
requirements.txt
README.md
DECISION_LOG.md
src/
└── skylark_bi/
    ├── core/
    └── agents/
        ├── query_agent/
        ├── monday_agent/
        ├── bi_agent/
        ├── resilience_agent/
        └── orchestrator/
tests/
├── phase2/
└── test_query_understanding.py
```

## Local Setup

```bash
git clone <repository-url>
cd skylark-bi-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set the required values in `.env`, then run the tests:

```bash
export PYTHONPATH="$PWD/src"
pytest -q
```

Start the Streamlit application with:

```bash
streamlit run app.py
```

## Environment Variables

| Variable                      | Purpose                          |
| ----------------------------- | -------------------------------- |
| `MONDAY_API_TOKEN`            | Monday.com API token             |
| `MONDAY_DEALS_BOARD_ID`       | Deals board ID                   |
| `MONDAY_WORK_ORDERS_BOARD_ID` | Work Orders board ID             |
| `GROQ_API_KEY`                | Enables Groq query understanding |
| `GROQ_MODEL`                  | Groq model name                  |
| `GROQ_TIMEOUT`                | Groq request timeout in seconds  |

The optional Monday.com settings `MONDAY_API_VERSION`, `MONDAY_API_TIMEOUT`, `MONDAY_MAX_RETRIES`, and `MONDAY_PAGE_SIZE` are also supported. Actual secrets must never be committed to GitHub.

## Monday.com Configuration

Local execution and deployment require:

- A Monday.com API token
- The Deals board ID
- The Work Orders board ID
- Read access to both boards

The configured token is used to retrieve schemas and items only. The application does not create, update, or delete Monday.com records.

## Testing

The current test suite contains **29 passing tests**, including focused coverage for Monday.com integration, board mapping, reconciliation, and Groq query-understanding fallback behavior. Unit tests do not make real Groq API calls.

## Deployment

The application is deployable as a Streamlit app. Configure Monday.com and Groq values through Streamlit Secrets rather than committing a `.env` file or credentials. The application reads Groq settings from Streamlit Secrets and uses them for query planning only.

## Security

- Monday.com integration is read-only.
- Credentials are not hardcoded in source code.
- Secrets are supplied through environment variables or Streamlit Secrets.
- Groq receives query-planning context, not the full business dataset or Monday.com records.

## Limitations and Future Improvements

Potential future improvements include:

- Richer historical trend analysis
- Forecasting
- More advanced entity resolution
- Receivables aging
- Anomaly detection
- Richer visualizations
- Authentication and role-based access control
- Production observability
