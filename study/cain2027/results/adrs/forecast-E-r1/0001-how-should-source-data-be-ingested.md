# How should source data be ingested?

* System: Retail demand forecasting

## Context and Problem Statement

The system forecasts weekly demand, so the pipeline needs a repeatable way to collect data for each run.

## Decision Drivers

* Weekly forecasts
* Repeatable runs

## Considered Options

* Data ingestion in batches (`v:7.3`)
* Streamed data ingestion (`v:7.1`)

## Decision Outcome

Chosen option: "Data ingestion in batches" (`v:7.3`).

Batch ingestion fits the weekly forecast cycle and makes each run’s inputs easier to reproduce (d:7, v:7.3).

### Consequences

* Runs consume collected input batches.
* Input timing must be coordinated with the weekly run.

## Pros and Cons of the Options

### Data ingestion in batches

* Good, because Fits weekly inputs
* Good, because Supports repeatable runs
* Bad, because Data may be stale
* Sources: `d:7`, `v:7.3`

### Streamed data ingestion

* Good, because Continuous updates
* Bad, because More operational complexity
* Sources: `d:7`, `v:7.1`
