# Monday Integration

## Purpose

Phase 2 provides a read-only Monday.com integration layer for the Skylark BI Agent. Monday.com is the runtime source of truth for Deals and Work Orders data, and this module gives later agents a clean service boundary without exposing GraphQL response structures or Monday column IDs.

## Architecture

```text
User/Orchestrator
        |
        v
MondayIntegrationService
        |
        +--> BoardReader
        |       |
        |       v
        |   MondayClient
        |       |
        |       v
        |   Monday GraphQL API
        |
        +--> Mapper
        |
        +--> Reconciliation
        |
        v
Canonical Deal / WorkOrder models
```

`MondayIntegrationService` is the public entry point. It delegates low-level HTTP and GraphQL execution to `MondayClient`, board/schema/item retrieval to `MondayBoardReader`, canonical mapping to `mapper.py`, and record-level comparison to `reconciliation.py`.

## Authentication

Authentication uses the Monday API token from environment configuration. Tokens must never be committed to source control or included in documentation. The local `.env` file is loaded by configuration code, but `.env` itself should remain private.

## Environment Variables

Required:

- `MONDAY_API_TOKEN`

Optional:

- `MONDAY_API_VERSION`
- `MONDAY_DEALS_BOARD_ID`
- `MONDAY_WORK_ORDERS_BOARD_ID`
- `MONDAY_API_TIMEOUT`
- `MONDAY_MAX_RETRIES`
- `MONDAY_PAGE_SIZE`

Board IDs are configuration values. They may appear in setup examples, but application logic must read them from environment configuration.

## Board Discovery

`MondayIntegrationService.discover_board(board_id)` returns a concise dictionary containing board identity, state, permissions, and column metadata. This is useful for setup verification and future agent inspection.

## Schema Retrieval

`MondayIntegrationService.get_board_schema(board_id)` returns a typed `MondayBoard` model containing board metadata and `MondayColumn` entries. Schema retrieval is separate from item retrieval so callers can inspect the board shape independently.

## Dynamic Item Retrieval

`MondayBoardReader.read_board(board_id)` reads the board schema and all available items, returning `BoardData`. Items are represented as `MondayItem` objects with Monday system fields and raw `column_values`.

The Monday agent runtime does not read CSV files. CSVs may be used by standalone validation or reconciliation scripts only when explicitly needed.

## Cursor-Based Pagination

Item retrieval uses Monday's cursor-based pagination. The first page is read through `items_page`, and subsequent pages are read through `next_items_page` until no cursor remains. `MONDAY_PAGE_SIZE` is capped at Monday's supported page size.

## Error Handling

HTTP, authentication, permission, rate limit, GraphQL, and connection failures are converted into Monday-specific domain exceptions from `errors.py`. Future agents should catch `MondayIntegrationError` or a more specific subclass instead of handling raw `requests` exceptions.

## Canonical Mapping

The mapper converts `MondayItem` plus `MondayBoard` schema into canonical `Deal` and `WorkOrder` models from `skylark_bi.core.models`.

Mapping is based on Monday column titles and optional configured mappings, not hardcoded Monday column IDs. The Monday system `Name` field maps to the canonical item/deal name where appropriate.

Parsing is defensive:

- Missing values become `None`.
- Unknown or unavailable columns become `None`.
- Malformed numeric values become `None`.
- Malformed dates become `None`.
- Raw Monday text values are preserved on canonical models in `raw_values`.

The mapper intentionally avoids aggressive business normalization. Deeper cleanup belongs to the future Resilience Agent.

## Reconciliation

`reconciliation.py` compares source records with Monday records using deterministic normalized fingerprints. It does not create, update, delete, or otherwise modify Monday records.

Deals use:

- Deal Name
- Owner code
- Client Code
- Deal Status
- Created Date

Work Orders use:

- Deal name masked / canonical deal name
- Customer Name Code
- Serial #
- Nature of Work

Normalization is limited to safe comparison behavior: trimming whitespace, case folding, collapsing whitespace, and using a consistent missing-value representation. Blank source names are classified as incomplete rather than invented.

The structured result includes:

- `source_count`
- `monday_count`
- `matched_count`
- `missing_from_monday`
- `monday_only`
- `duplicate_source_records`
- `incomplete_source_records`

Duplicate source fingerprints are reported separately from records that are genuinely absent from Monday.

## Read-Only Guarantee

The Monday agent exposes only read, map, and reconcile operations. It does not expose create, update, or delete operations for items or boards.

Explicitly unsupported:

- Create item
- Update item
- Delete item
- Create board
- Update board
- Delete board

## Future Agent Usage

The Orchestrator, Query Agent, BI Agent, and Resilience Agent should use `MondayIntegrationService` as their boundary. They should consume canonical `Deal`, canonical `WorkOrder`, and reconciliation result models instead of depending on GraphQL payloads, Monday item internals, or Monday column IDs.
