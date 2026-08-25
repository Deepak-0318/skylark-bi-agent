# Skylark BI Agent — Architecture

## Phase 1 Data Understanding

```text
Deals CSV ───────────┐
                     │
                     ▼
                Dataset Loader
                     │
Work Orders CSV ────┘
                     │
                     ▼
              Dataset Profiler
                     │
                     ▼
              Quality Analyzer
                     │
                     ▼
           Relationship Analyzer
                     │
                     ▼
             Metric Catalog
                     │
                     ▼
          Canonical Data Model