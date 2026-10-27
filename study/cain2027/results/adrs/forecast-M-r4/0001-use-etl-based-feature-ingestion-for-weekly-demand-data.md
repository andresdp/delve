# Use ETL-based feature ingestion for weekly demand data

* System: Retail demand forecasting

## Context and Problem Statement

The pipeline consumes historical store and product records on a weekly cadence. The brief does not require event-time processing.

## Decision Drivers

* Weekly data cadence
* Repeatable inputs

## Considered Options

* ETL-based feature ingestion (`v:21.1`)
* Streaming feature ingestion (`v:21.2`)

## Decision Outcome

Chosen option: "ETL-based feature ingestion" (`v:21.1`).

ETL matches the weekly batch workload and avoids introducing streaming operations for a freshness requirement the brief does not state.

### Consequences

* Source extracts must be available on schedule.

## Pros and Cons of the Options

### ETL-based feature ingestion

* Good, because Batch-friendly
* Good, because Row-level features
* Bad, because Depends on source extracts

### Streaming feature ingestion

* Good, because Continuous updates
* Good, because Low-latency inputs
* Bad, because Extra streaming operations
