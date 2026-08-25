# Skylark BI Agent — Decision Log

## 1. Key Assumptions

### Monday.com as the system of record
The solution assumes that Monday.com is the primary source of truth for business data. The prototype reads the Deals and Work Orders boards in read-only mode and does not modify Monday.com data.

### Two primary business datasets
The prototype focuses on two datasets:
- Deals — sales pipeline and opportunity information.
- Work Orders — operational, billing, collection, and receivables information.

These datasets were sufficient to answer the required founder-level business questions.

### Canonical data models
Monday.com records are mapped into canonical `Deal` and `WorkOrder` models before analysis. This separates Monday-specific schemas from the business intelligence layer and makes the analytical logic independent of the source representation.

### Deterministic query understanding
The prototype uses a deterministic query-understanding layer rather than depending on an external LLM API. This was an intentional choice for reliability, reproducibility, and avoiding API-key dependency during evaluation.

---

## 2. Key Trade-offs

### Deterministic rules vs. LLM-based interpretation

The prototype uses rule-based intent classification and entity extraction.

**Why:**
- No external model/API dependency.
- Predictable results.
- Easier to test.
- Lower operational cost.
- Suitable for a constrained business-question vocabulary.

**Trade-off:**
Natural-language flexibility is lower than a production LLM-powered system.

With more time, an LLM could be introduced behind the same query-agent interface while retaining deterministic validation and safety checks.

### Read-only integration vs. write-back automation

The Monday.com integration is intentionally read-only.

**Why:**
The assignment requires business intelligence and decision support, not operational automation. Read-only access reduces the risk of accidentally modifying production business data.

### Founder-level summaries vs. detailed BI dashboards

The UI prioritizes a small number of high-value metrics rather than exposing every available field.

The goal is to answer questions such as:
- How is the pipeline looking?
- Which sector has the strongest pipeline?
- What is outstanding in receivables?
- What should leadership be concerned about?

This keeps the interface focused on decision-making rather than data exploration.

---

## 3. Interpretation of "Leadership Updates"

A leadership update was interpreted as a concise executive-level summary combining:

1. Sales pipeline health
2. Weighted pipeline
3. Operational workload
4. Billing/collection position
5. Financial risks requiring attention

The prototype therefore combines Deal and Work Order metrics for leadership-oriented questions and surfaces insights and risks rather than returning raw records.

For example, a leadership update can highlight:
- Total pipeline value
- Weighted pipeline
- Number of active deals
- Work-order volume
- Billing position
- Outstanding receivables
- Areas requiring leadership attention

---

## 4. Resilience and Data Quality

The system was designed to tolerate incomplete or inconsistent source data.

Examples include:
- Missing numeric values
- Missing dates
- Empty Monday.com fields
- Different column naming conventions
- Nullable financial fields
- Unrecognized natural-language questions

The mapping layer performs defensive parsing before data reaches the BI layer.

This prevents source-data irregularities from directly causing failures in business analysis.

---

## 5. What I Would Do Differently With More Time

### LLM-powered natural-language understanding
Introduce an LLM behind the existing query-agent abstraction for more flexible questions while retaining deterministic validation.

### More advanced analytics
Add:
- Trend analysis
- Period-over-period comparisons
- Forecasting
- Deal aging
- Pipeline conversion analysis
- Sector benchmarking
- Receivables aging
- Anomaly detection

### Richer visualizations
Add charts for:
- Pipeline by sector
- Pipeline by stage
- Monthly pipeline movement
- Billing vs. collection
- Receivables aging
- Work-order status

### Production observability
Add structured logging, request tracing, performance metrics, and monitoring for the deployed application.

### Authentication and access control
A production version would integrate authentication and role-based access control so that sensitive business information is only visible to authorized users.

---

## 6. Final Design Principle

The prototype prioritizes:

**Reliable business answers → transparent calculations → safe data access → simple executive UX**

rather than maximizing model complexity.

This makes the prototype suitable for demonstrating the core concept while providing a clear path toward a production-grade BI agent.