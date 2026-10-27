# Process retail demand in weekly batches

* System: Retail demand forecasting

## Context and Problem Statement

The system produces weekly forecasts per store and product. The design space offers batch and real time processing.

## Decision Drivers

* Weekly forecast cadence
* Reproducibility

## Considered Options

* Batch-based data processing (`v:15.1`)
* Real-time, stream-based data processing (`v:15.2`)

## Decision Outcome

Chosen option: "Batch-based data processing" (`v:15.1`).

Weekly outputs do not require continuous processing, so batch processing fits the stated cadence and simplifies repeatable runs.

### Consequences

* Schedule data preparation and forecasting for each weekly period.
* Late arriving data needs an explicit rerun policy.

## Pros and Cons of the Options

### Batch-based data processing

* Good, because Matches weekly cadence
* Good, because Supports repeatable runs
* Bad, because Results arrive on batch schedule
* Sources: `d:15`, `v:15.1`

### Real-time, stream-based data processing

* Good, because Processes events continuously
* Bad, because Adds streaming complexity
* Sources: `d:15`, `v:15.2`
