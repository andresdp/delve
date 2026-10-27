# Use batch processing for weekly demand data

* System: Retail demand forecasting

## Context and Problem Statement

The system forecasts weekly demand per store and product, so the brief calls for a recurring weekly run. The design space compares batch processing with real-time stream processing (d:15).

## Decision Drivers

* Weekly forecasts
* Reproducible history

## Considered Options

* Batch-based data processing (`v:15.1`)
* Real-time, stream-based data processing (`v:15.2`)

## Decision Outcome

Chosen option: "Batch-based data processing" (`v:15.1`).

The weekly forecast cadence supports batch processing; the brief gives no real-time requirement (d:15, v:15.1).

### Consequences

* Run processing on a weekly schedule.
* Keep historical inputs available for reruns.

## Pros and Cons of the Options

### Batch-based data processing

* Good, because Fits weekly cadence
* Bad, because Not real-time
* Sources: `d:15`, `v:15.1`

### Real-time, stream-based data processing

* Good, because Processes streams continuously
* Bad, because Adds needless complexity
* Sources: `d:15`, `v:15.2`
