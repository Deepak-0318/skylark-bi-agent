# Skylark BI Agent — Decision Log

## 1. Overview

Skylark BI Agent is a read-only, agentic business intelligence prototype designed to provide founder-level insights from Monday.com business data.

The system connects dynamically to two Monday.com boards:

- Deals
- Work Orders

Users interact with the system using natural-language business questions. A query-understanding layer converts the question into a structured query plan, business calculations are performed deterministically, and the final response presents metrics, insights, risks, and caveats.

---

## 2. Key Assumptions

### Monday.com is the system of record

The prototype assumes Monday.com is the primary source of truth for the business data.

The application dynamically retrieves data from Monday.com using its API and operates in read-only mode.

No business dataset is hardcoded into the application.

### Two primary business datasets

The prototype focuses on:

- **Deals** — sales opportunities, pipeline value, probability, stages, sectors, and ownership.
- **Work Orders** — operational execution, billing, collections, receivables, and work-order information.

These two datasets provide sufficient coverage for the required founder-level business questions.

### Canonical business models

Monday.com records are mapped into canonical:

- `Deal`
- `WorkOrder`

models before reaching the BI layer.

This separates Monday-specific column structures from business logic and allows the analytical layer to operate on consistent objects.

### Financial values

Financial values are treated as analytical values supplied by the connected Monday.com boards.

The system aggregates and compares these values but does not invent missing financial information.

---

## 3. Query Understanding Approach

### Groq LLM for natural-language interpretation

Groq is used to improve natural-language query understanding.

The LLM receives:

- the user's question
- the allowed intents
- allowed datasets
- allowed metrics
- allowed filters
- allowed grouping dimensions

It returns a structured JSON query plan.

The plan can contain:

- intent
- datasets
- filters
- date range
- metrics
- grouping
- sorting
- confidence
- clarification state

### LLM does not calculate business metrics

A key architectural decision was to separate interpretation from computation.

The LLM is responsible for:

> Understanding what the user is asking.

The deterministic BI layer is responsible for:

> Calculating the actual business metrics from Monday.com data.

This reduces the risk of hallucinated financial numbers and makes calculations reproducible.

### Validation boundary

LLM output is treated as untrusted input.

The validation layer checks:

- supported intents
- supported datasets
- supported metrics
- supported filters
- supported grouping
- valid confidence values
- valid sorting
- valid limits
- valid clarification state
- valid date ranges

Invalid plans are rejected and the system can fall back to deterministic query understanding.

---

## 4. Key Trade-offs

### LLM flexibility vs. deterministic reliability

Using an LLM provides significantly better natural-language interpretation than a purely rule-based system.

However, allowing the LLM to directly calculate business results would introduce unnecessary risk.

Therefore, the system uses:

**LLM → Query Plan → Validation → Deterministic BI**

rather than:

**LLM → Business Answer**

This provides greater flexibility while keeping business calculations transparent.

### Read-only integration vs. write automation

The Monday.com integration is intentionally read-only.

This was chosen because the assignment focuses on business intelligence and decision support rather than operational automation.

Read-only access also minimizes the risk of modifying production business records.

### Founder-level summaries vs. complete data exploration

The interface prioritizes high-value executive metrics and insights rather than exposing every raw Monday.com field.

The goal is to help leadership answer questions quickly rather than reproduce a complete BI dashboard.

---

## 5. Data Resilience Decisions

The system is designed to tolerate incomplete and inconsistent source data.

The mapping and validation layers handle:

- missing values
- null values
- empty Monday.com fields
- inconsistent date formats
- numeric formatting
- currency symbols
- percentage symbols
- alternative column names
- missing optional fields

When information is unavailable, the system avoids inventing values and can surface caveats or return `N/A`.

### Column-name normalization

Monday.com column titles can vary between boards.

The mapper therefore supports aliases and normalized column-name matching.

For example, business fields may have multiple Monday representations while still mapping to one canonical model field.

### LLM resilience

Malformed LLM output is rejected rather than passed directly into the BI layer.

This prevents unsupported metrics, filters, or datasets from reaching deterministic business calculations.

---

## 6. Cross-Board Analysis

The system supports questions requiring information from both Deals and Work Orders.

For example:

> "Compare our sales pipeline with work order execution."

The query planner can identify both datasets.

The BI layer then calculates metrics from:

- Deals
- Work Orders

without requiring the LLM to see or calculate the underlying business records.

---

## 7. Interpretation of "Leadership Updates"

"Leadership update" was interpreted as a concise executive-level summary of the current business position.

The summary can combine:

### Sales

- Deal count
- Pipeline value
- Weighted pipeline
- Pipeline concentration

### Operations

- Work-order count
- Execution-related metrics

### Financial position

- Billed value
- Amount to be billed
- Collected value when available
- Outstanding receivables

### Risks

Examples include:

- high outstanding receivables
- low weighted pipeline relative to total pipeline
- operational or billing concerns
- concentration in particular business sectors

The intent is to surface information that could require leadership attention rather than simply returning raw rows.

---

## 8. Security and Access Decisions

The prototype uses:

- read-only Monday.com access
- environment variables for local secrets
- Streamlit Secrets for hosted deployment
- Groq API credentials stored outside source code

Actual API keys are not committed to the GitHub repository.

The Groq query-planning layer receives the user's business question and the allowed query vocabulary rather than the complete Monday.com business dataset.

---

## 9. What Would Be Improved With More Time

### More advanced analytics

Future versions could add:

- historical trend analysis
- month-over-month and quarter-over-quarter comparisons
- pipeline conversion analysis
- deal aging
- forecasting
- sector benchmarking
- receivables aging
- anomaly detection

### Better entity resolution

Cross-board relationships could be strengthened through more sophisticated entity resolution between:

- Deal names
- Work-order names
- Client identifiers
- Owner identifiers

### Richer visualizations

The prototype could be extended with:

- pipeline by sector
- pipeline by stage
- billing vs. collection trends
- receivables aging
- work-order execution status
- historical pipeline movement

### Production observability

A production implementation should include:

- structured logging
- request tracing
- API latency monitoring
- error monitoring
- model usage monitoring
- caching and rate-limit handling

### Authentication and authorization

A production deployment should include authentication and role-based access control so that sensitive business information is only available to authorized users.

---

## 10. Current Scope

The prototype intentionally focuses on the required business intelligence workflow:

```text
Natural-language question
        ↓
Groq query understanding
        ↓
Validated query plan
        ↓
Dynamic Monday.com retrieval
        ↓
Canonical business models
        ↓
Deterministic BI calculations
        ↓
Insights and risk detection
        ↓
Founder-level response