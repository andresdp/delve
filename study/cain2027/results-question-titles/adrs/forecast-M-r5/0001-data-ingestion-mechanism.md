# Data ingestion mechanism

* System: Retail demand forecasting

## Context and Problem Statement

Weekly forecasts depend on recurring historical sales and product/store records. The brief does not specify source systems, so choose an ingestion pattern suited to periodic data.

## Decision Drivers

* Weekly cadence
* Historical reproducibility
* Small team

## Considered Options

* ETL-based feature ingestion (`v:21.1`)
* Streaming feature ingestion (`v:21.2`)

## Decision Outcome

Chosen option: "ETL-based feature ingestion" (`v:21.1`).

A batch extraction and transformation path aligns with weekly forecasting and avoids introducing streaming operations absent a freshness requirement. The design point check reports no warnings for this choice; the combination is unattested.

### Consequences

* Ingestion runs on a schedule.
* Source snapshots and transformations need versioning.

## Pros and Cons of the Options

### ETL-based feature ingestion

* Good, because Fits periodic records
* Good, because Supports batch preparation
* Bad, because Upstream schema changes

### Streaming feature ingestion

* Good, because Continuous updates
* Good, because Event-driven inputs
* Bad, because More moving parts
