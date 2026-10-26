# How should demand data be processed?

* System: Retail demand forecasting

## Context and Problem Statement

The system produces forecasts weekly for each store and product. The brief does not require real-time results.

## Decision Drivers

* Weekly cadence
* Small team
* Repeatable runs

## Considered Options

* Batch-based data processing (`v:15.1`)
* Real-time, stream-based data processing (`v:15.2`)

## Decision Outcome

Chosen option: "Batch-based data processing" (`v:15.1`).

Weekly forecasts fit scheduled batches, keeping the pipeline proportionate to a three-person team (d:15, v:15.1).

### Consequences

* Forecast freshness follows the batch schedule.
* Late data may require a rerun.

## Pros and Cons of the Options

### Batch-based data processing

* Good, because Matches weekly cadence
* Good, because Simpler operations
* Bad, because Results wait for batch
* Sources: `d:15`, `v:15.1`

### Real-time, stream-based data processing

* Good, because Low-latency updates
* Bad, because More operational work
* Sources: `d:15`, `v:15.2`
