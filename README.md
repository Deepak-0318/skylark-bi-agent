# Skylark BI Agent

> Founder-level business intelligence powered by Monday.com.

Skylark BI Agent is a read-only, agentic business intelligence prototype that connects to Monday.com, understands natural-language business questions, analyzes Deals and Work Orders, and returns concise founder-level insights.

The goal is to turn operational data into decision-ready business intelligence without requiring leadership to manually inspect boards, combine datasets, or calculate metrics.

---

## Live Prototype

### Hosted Application

**https://skylark-bi-agent-01.streamlit.app**

The hosted prototype can be tested directly without installing the project locally.

The application provides a natural-language interface for asking business questions about the Deals and Work Orders data available through Monday.com.

---

# Problem

Business data often exists inside operational tools such as Monday.com, but leadership still has to manually inspect boards and calculate metrics before making decisions.

Skylark BI Agent provides a natural-language interface for questions such as:

- How is our pipeline looking?
- Which sector has the strongest pipeline?
- How is the mining sector pipeline?
- What is our outstanding receivable?
- How many deals do we have?
- Give me a leadership update.
- What should leadership be concerned about?

Instead of returning raw records, the system converts the available operational data into:

- Metrics
- Insights
- Risks
- Caveats
- Executive-level summaries

---

# Architecture

```text
                    ┌─────────────────────┐
                    │     Streamlit UI    │
                    │       app.py        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     Orchestrator    │
                    │                     │
                    │ Coordinates agents  │
                    └──────────┬──────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
                ▼                             ▼
      ┌──────────────────┐          ┌──────────────────┐
      │   Query Agent    │          │   Monday Agent   │
      │                  │          │                  │
      │ Intent           │          │ Board discovery  │
      │ Entities         │          │ Item retrieval   │
      │ Filters          │          │ Pagination       │
      │ Planning         │          │ Data mapping     │
      │ Validation       │          │ Reconciliation   │
      └─────────┬────────┘          └─────────┬────────┘
                │                             │
                │                             ▼
                │                    ┌─────────────────┐
                │                    │ Canonical       │
                │                    │ Business Models │
                │                    │                 │
                │                    │ Deal            │
                │                    │ WorkOrder       │
                │                    └────────┬────────┘
                │                             │
                └──────────────┬──────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      BI Agent       │
                    │                     │
                    │ Filters             │
                    │ Metrics             │
                    │ Aggregations        │
                    │ Comparisons         │
                    │ Insights            │
                    │ Leadership analysis │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Resilience Agent   │
                    │                     │
                    │ Validation          │
                    │ Data quality        │
                    │ Readiness           │
                    │ Impact analysis     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Executive Response │
                    │                     │
                    │ Metrics             │
                    │ Insights            │
                    │ Risks               │
                    │ Caveats             │
                    └─────────────────────┘

###  Agent Architecture

The system is divided into specialized agents rather than implementing all logic in a single component.

1. Query Understanding Agent

The Query Agent converts natural-language questions into structured analytical plans.

It identifies:

Intent
Relevant datasets
Entities
Filters
Metrics
Grouping
Confidence
Clarification requirements

For example:

User:
How is the mining sector pipeline?

        ↓

Intent:
pipeline_health

        ↓

Dataset:
deals

        ↓

Filter:
sector = Mining

        ↓

Metrics:
pipeline_value
weighted_pipeline
deal_count

This creates a structured representation that the BI layer can process deterministically.

2. Monday.com Integration Agent

The Monday Agent provides read-only access to Monday.com.

Its responsibilities include:

Authentication
Board discovery
Board schema retrieval
Item retrieval
Pagination
Column mapping
Data normalization
Reconciliation
Error handling

The integration uses the Monday.com GraphQL API.

The agent converts Monday.com-specific records into canonical business models before analysis.

3. Canonical Business Models

The system separates the source-specific Monday.com schema from the analytical layer.

The primary canonical models are:

Deal
WorkOrder

The flow is:

Monday.com records
        ↓
Monday Agent
        ↓
Mapping layer
        ↓
Canonical models
        ↓
BI Agent

This allows the analytical layer to operate on stable business objects instead of being tightly coupled to Monday.com column names.

4. Business Intelligence Agent

The BI Agent performs deterministic business analysis over the canonical datasets.

Its responsibilities include:

Filtering
Metric calculation
Aggregation
Sector analysis
Pipeline analysis
Receivables analysis
Comparisons
Insight generation
Risk identification
Leadership analysis
Deal metrics

The system supports metrics such as:

Deal count
Pipeline value
Weighted pipeline
Work Order metrics

The system supports metrics such as:

Work-order count
Billed value
Collected value
Amount to be billed
Outstanding receivables
5. Data Resilience Agent

The Resilience Agent protects the analytical pipeline from incomplete or inconsistent operational data.

Its responsibilities include:

Data validation
Type inference
Data quality analysis
Date normalization
Readiness assessment
Quality filtering
Business impact analysis

The system uses defensive parsing for:

Dates
Numeric values
Optional strings
Missing values

The resilience layer also provides caveats when the available data is insufficient for a reliable analysis.

6. Orchestrator Agent

The Orchestrator coordinates the end-to-end workflow.

Natural-language question
          ↓
Query understanding
          ↓
Structured query plan
          ↓
Monday.com data retrieval
          ↓
Canonical business models
          ↓
BI analysis
          ↓
Resilience / validation
          ↓
Executive response

The Orchestrator keeps the individual agent responsibilities separated while providing a single application-level workflow.

Data Sources

The prototype currently works with two primary Monday.com boards.

Deals Board

The Deals board is used for:

Pipeline analysis
Deal count
Pipeline value
Weighted pipeline
Deal status
Deal stage
Sector analysis
Close-date analysis
Work Orders Board

The Work Orders board is used for:

Operational workload
Billing analysis
Collection analysis
Amount to be billed
Outstanding receivables
Execution status
Sector analysis
Monday.com Configuration

The application requires access to the relevant Monday.com boards.

Required Boards

Two Monday.com boards are required:

Deals
Work Orders

The application only reads data from these boards.

Monday.com API Token

The application uses the Monday.com GraphQL API.

A Monday.com API token is required for local execution and deployment.

Create or obtain a Monday.com API token with access to the required boards.

The token must have sufficient permission to read the configured boards.

The application does not use the token to modify board data.

Required Environment Variables

Create a local .env file or configure environment variables using your deployment platform.

Required variables:

MONDAY_API_TOKEN=your_monday_api_token
MONDAY_API_VERSION=2026-07
MONDAY_DEALS_BOARD_ID=your_deals_board_id
MONDAY_WORK_ORDERS_BOARD_ID=your_work_orders_board_id

Optional configuration:

MONDAY_API_TIMEOUT=30
MONDAY_MAX_RETRIES=3
MONDAY_PAGE_SIZE=100
Security

Never commit the actual Monday.com API token to GitHub.

The .env file should remain ignored by Git.

For Streamlit deployment, use Streamlit Secrets instead of committing credentials to the repository.

Finding Monday.com Board IDs

Open the required board in Monday.com.

The board ID can be obtained from the board URL or Monday.com board information.

Configure:

MONDAY_DEALS_BOARD_ID=<Deals board ID>
MONDAY_WORK_ORDERS_BOARD_ID=<Work Orders board ID>

The application uses these IDs to discover the board schema and retrieve items.

Monday.com Column Mapping

The integration layer maps Monday.com columns into canonical business fields.

Deals

The Deals mapping supports fields including:

Name
Owner code
Client Code
Deal Status
Close Date
Closure Probability
Deal Value
Tentative Close Date
Deal Stage
Product deal
Sector/service
Created Date

The mapper supports alternate column names where appropriate.

Work Orders

The Work Orders mapping supports fields including:

Name
Customer Name Code
Serial #
Nature of Work
Last executed month of recurring project
Execution Status
Data Delivery Date
Date of PO/LOI
Document Type
Probable Start Date
Probable End Date
BD/KAM Personnel code
Sector
Type of Work
Software platform in deliverables
Last invoice date
Latest invoice number
Amount in Rupees
Billed Value
Collected Amount
Amount to be billed
Amount Receivable
AR Priority account
Quantity by Ops
Quantities as per PO
Quantity billed
Balance in quantity
Invoice Status
Expected Billing Month
Actual Billing Month
Actual Collection Month
WO Status
Collection status
Collection Date
Billing Status

The mapping layer handles missing and optional fields defensively.

Local Setup
Requirements
Python 3.12+
Monday.com account
Monday.com API token
Access to the Deals board
Access to the Work Orders board
1. Clone the repository
git clone https://github.com/Deepak-0318/skylark-bi-agent.git

cd skylark-bi-agent
2. Create a virtual environment
python3 -m venv .venv

Activate it:

macOS / Linux
source .venv/bin/activate
Windows
.venv\Scripts\activate
3. Install dependencies
pip install -r requirements.txt
4. Configure Python path

macOS / Linux:

export PYTHONPATH="$PWD/src"
5. Configure Monday.com credentials

For local development, configure the required environment variables or .env file:

MONDAY_API_TOKEN=your_token
MONDAY_API_VERSION=2026-07
MONDAY_DEALS_BOARD_ID=your_deals_board_id
MONDAY_WORK_ORDERS_BOARD_ID=your_work_orders_board_id
Running the Application

Start the Streamlit application:

streamlit run app.py

The application will be available locally at:

http://localhost:8501
Testing

The project includes automated tests covering the major components of the system.

Run the complete test suite:

export PYTHONPATH="$PWD/src"
pytest -q

Current regression test result:

32 passed

The test suite covers areas including:

Dataset loading
Data normalization
Dataset profiling
Data quality
Cross-board relationships
Monday.com client
Board discovery
Board pagination
Monday.com mapping
Reconciliation
Query understanding
BI analysis
Resilience functionality
Orchestration
Monday.com Integration Tests

The repository also contains scripts for testing the Monday.com integration.

Authentication
python scripts/test_monday_auth.py
Board connection
python scripts/test_monday_connection.py
Data retrieval
python scripts/test_monday_data.py
Data reconciliation
python scripts/reconcile_monday_data.py

These scripts are intended for local verification of the Monday.com integration.

Example Questions

The application supports natural-language business questions.

Pipeline
How is our pipeline looking?

Expected analysis includes:

Deal count
Pipeline value
Weighted pipeline
Pipeline insight
Sector Pipeline
How is the mining sector pipeline?

Expected analysis includes:

Mining deal count
Mining pipeline value
Weighted pipeline
Sector concentration insight
Receivables
What is our outstanding receivable?

Expected analysis includes:

Work-order count
Billed value
Amount to be billed
Outstanding receivables
Receivables risk
Leadership Update
Give me a leadership update.

The system combines sales and operational information into an executive-level summary.

Deal Count
How many deals do we have?

The system returns the currently available deal count.

Sector Comparison
Which sector has the strongest pipeline?

The system groups pipeline information by sector and identifies the strongest value concentration.

Leadership Update Interpretation

For this prototype, a leadership update is interpreted as a concise executive summary rather than a raw data report.

The response prioritizes:

Sales pipeline health
Weighted pipeline
Operational workload
Billing position
Outstanding receivables
Material risks

The objective is to answer:

What does leadership need to know right now?

rather than simply presenting all available data.

Data Resilience

Operational datasets can contain:

Missing values
Incomplete dates
Empty fields
Different column naming conventions
Invalid numeric values
Partially populated records

The Resilience Agent is designed to prevent these issues from unnecessarily breaking downstream analysis.

Examples include:

Raw Monday.com value
        ↓
Validation
        ↓
Normalization
        ↓
Canonical field
        ↓
BI analysis

When data is insufficient, the system can expose caveats rather than silently presenting unreliable conclusions.

Read-Only Design

The Monday.com integration is intentionally read-only.

The application:

Reads board schemas
Reads board items
Reads column values
Performs local analysis
Does not create Monday.com items
Does not update Monday.com items
Does not delete Monday.com data

This reduces the operational risk of the prototype.

Security

API credentials must never be committed to GitHub.

The following should remain private:

MONDAY_API_TOKEN

Local credentials should be stored using environment variables or .env.

For hosted deployment, credentials should be stored using the platform's secret-management mechanism.

For a production system, additional security controls should be introduced, including:

Authentication
Role-based access control
Secret rotation
Audit logging
Access policies
Monitoring
Rate limiting
Hosted Deployment

The prototype is deployed using Streamlit Community Cloud.

Live application:

https://skylark-bi-agent-01.streamlit.app

The deployed application can be tested without local installation.

The Monday.com API token and board IDs should be configured through Streamlit Secrets.

Example:

MONDAY_API_TOKEN = "your_token"
MONDAY_API_VERSION = "2026-07"
MONDAY_DEALS_BOARD_ID = "your_deals_board_id"
MONDAY_WORK_ORDERS_BOARD_ID = "your_work_orders_board_id"

Do not commit these values to the repository.

Project Structure
skylark-bi-agent/
│
├── app.py
├── README.md
├── DECISION_LOG.md
├── requirements.txt
├── .gitignore
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DATA_DICTIONARY.md
│   ├── DATASET_ANALYSIS.md
│   └── MONDAY_INTEGRATION.md
│
├── data/
│   ├── raw/
│   └── processed/
│
├── scripts/
│   ├── inspect_deal_duplicates.py
│   ├── inspect_relationships.py
│   ├── reconcile_monday_data.py
│   ├── run_phase1.py
│   ├── test_monday_auth.py
│   ├── test_monday_connection.py
│   └── test_monday_data.py
│
├── tests/
│   ├── phase1/
│   └── phase2/
│
└── src/
    └── skylark_bi/
        │
        ├── agents/
        │   │
        │   ├── bi_agent/
        │   ├── monday_agent/
        │   ├── orchestrator/
        │   ├── query_agent/
        │   └── resilience_agent/
        │
        ├── core/
        │
        └── phase1/
Development Phases

The project was implemented as a sequence of focused phases.

Phase 1 — Dataset Understanding

Implemented:

Dataset loading
Normalization
Profiling
Data quality analysis
Cross-board relationship analysis
Business metric catalog

Outputs include:

deals_profile.json
work_orders_profile.json
data_quality_report.json
relationship_report.json
metric_catalog.json
Phase 2 — Monday.com Integration

Implemented:

Monday.com authentication
API client
Board discovery
Board schema retrieval
Pagination
Item retrieval
Data mapping
Reconciliation
Error handling
Phase 3 — Data Resilience

Implemented:

Type inference
Date normalization
Validation
Data quality filtering
Readiness assessment
Business impact analysis
Resilience service
Phase 4 — Query Understanding

Implemented:

Intent detection
Entity extraction
Dataset identification
Filter extraction
Metric planning
Query validation
Clarification handling
Phase 5 — Business Intelligence

Implemented:

Filtering
Metrics
Aggregations
Comparisons
Insights
Risk identification
Leadership analysis
Phase 6 — Orchestration

Implemented:

Agent coordination
Query-to-analysis workflow
Result aggregation
Executive response generation
Caveat propagation
Phase 7 — Conversational UI

Implemented using Streamlit:

Natural-language input
Query execution
Executive response
Metrics
Insights
Risks
Caveats
Design Principles

The system follows a few core design principles.

1. Read-only by default

The prototype does not modify operational data.

2. Deterministic business calculations

Business metrics are calculated through explicit Python logic rather than relying on an LLM to perform financial calculations.

3. Separation of concerns

Each agent has a focused responsibility.

Query Agent
     ↓
Understanding

Monday Agent
     ↓
Data access

Resilience Agent
     ↓
Data reliability

BI Agent
     ↓
Business analysis

Orchestrator
     ↓
Coordination

Streamlit
     ↓
User interaction
4. Canonical data models

Source-specific schemas are converted into stable business models before analytical processing.

5. Explicit caveats

The system is designed to surface data limitations rather than silently treating missing information as zero or complete information.

Limitations

This prototype intentionally focuses on the core business intelligence workflow.

Current limitations include:

Rule-based query understanding rather than a production-grade LLM
Limited natural-language coverage
Limited historical trend analysis
No write operations to Monday.com
No production authentication layer
No role-based access control
Limited visualization
Limited anomaly detection
No persistent conversational memory

These limitations are acceptable for the prototype and provide a clear path for future development.

Future Improvements

With additional development time, the following improvements could be added.

Natural Language
LLM-powered query understanding
More flexible business terminology
Conversational follow-up questions
Context-aware multi-turn conversations
Analytics
Period-over-period comparisons
Pipeline forecasting
Deal aging
Conversion rates
Receivables aging
Anomaly detection
Forecast accuracy
Visualization
Pipeline by sector
Pipeline by stage
Monthly trends
Billing vs. collection
Receivables aging
Work-order status dashboards
Production Readiness
User authentication
Role-based access control
Structured logging
Observability
Audit trails
Secret rotation
Automated reports
Scheduled leadership summaries
Submission Deliverables

The project provides the required submission components.

Deliverable	Status
Hosted Prototype	Complete
Public Application Link	Complete
Source Code	Complete
README	Complete
Monday.com Setup Instructions	Complete
Automated Tests	Complete
Decision Log	Included separately
Repository

GitHub:

https://github.com/Deepak-0318/skylark-bi-agent

Live Prototype:

https://skylark-bi-agent-01.streamlit.app