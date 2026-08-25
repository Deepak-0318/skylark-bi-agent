# Skylark BI Agent — Data Dictionary

## Deals Board

| Field | Business Meaning | Analytical Role |
|---|---|---|
| Deal Name | Deal identifier/name | Deal identity |
| Owner code | Sales owner identifier | Owner analysis |
| Client Code | Client identifier | Client analysis |
| Deal Status | Current deal status | Pipeline status |
| Close Date (A) | Actual close date | Historical timing |
| Closure Probability | Qualitative closure confidence | Forecast context |
| Masked Deal value | Anonymized deal value | Pipeline value |
| Tentative Close Date | Expected close date | Forecast timing |
| Deal Stage | Current sales stage | Funnel analysis |
| Product deal | Product/service associated with deal | Product analysis |
| Sector/service | Business sector | Sector analysis |
| Created Date | Deal creation date | Pipeline timing |

### Important quality considerations

- Close Date is heavily incomplete.
- Closure Probability is qualitative (`High`, `Medium`, `Low`) and should not be converted to percentages without an explicit business rule.
- Masked Deal value is substantially incomplete.
- Deal Stage is complete and highly reliable.
- Sector/service is highly complete.

---

## Work Orders Board

| Field | Business Meaning | Analytical Role |
|---|---|---|
| Deal name masked | Associated deal | Cross-board relationship |
| Customer Name Code | Customer identifier | Customer analysis |
| Serial # | Work order identifier | Work-order identity |
| Nature of Work | Nature/category of work | Operational analysis |
| Execution Status | Current execution state | Execution analysis |
| Data Delivery Date | Data delivery date | Operational timing |
| Date of PO/LOI | Order authorization date | Order timing |
| Document Type | PO/LOI/document type | Order classification |
| Probable Start Date | Expected project start | Forecast timing |
| Probable End Date | Expected project end | Forecast timing |
| BD/KAM Personnel code | Responsible owner | Owner analysis |
| Sector | Business sector | Sector analysis |
| Type of Work | Work category | Operational analysis |
| Amount in Rupees | Order value | Financial analysis |
| Billed Value | Amount billed | Billing analysis |
| Collected Amount | Amount collected | Collection analysis |
| Amount to be billed | Remaining billing | Billing analysis |
| Amount Receivable | Outstanding receivable | Cash/AR analysis |
| Quantity by Ops | Operational quantity | Quantity analysis |
| Quantities as per PO | Contract quantity | Quantity analysis |
| Quantity billed | Quantity invoiced | Billing progress |
| Balance in quantity | Remaining quantity | Execution progress |
| Invoice Status | Invoice state | Billing analysis |
| Billing Status | Billing workflow state | Billing analysis |

### Important quality considerations

Several billing and collection fields have significant missingness.

The following fields are completely empty in the provided dataset:

- Expected Billing Month
- Actual Collection Month
- Collection status
- Collection Date

These fields must not be used to produce unsupported conclusions.