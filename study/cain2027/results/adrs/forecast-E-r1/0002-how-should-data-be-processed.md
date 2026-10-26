# How should data be processed?

* System: Retail demand forecasting

## Context and Problem Statement

Demand features and forecasts are organized around weekly periods, with no requirement for immediate results.

## Decision Drivers

* Weekly cadence
* Pipeline repeatability

## Considered Options

* Batch-based data processing (`v:15.1`)
* Real-time, stream-based data processing (`v:15.2`)

## Decision Outcome

Chosen option: "Batch-based data processing" (`v:15.1`).

Weekly outputs favor bounded batch runs over continuous processing (d:15, v:15.1).

### Consequences

* Data processing runs on a weekly schedule.
* Late arriving data may require a rerun.

## Pros and Cons of the Options

### Batch-based data processing

* Good, because Matches weekly cadence
* Good, because Simple run boundaries
* Bad, because No immediate updates
* Sources: `d:15`, `v:15.1`

### Real-time, stream-based data processing

* Good, because Processes updates continuously
* Bad, because Unneeded for weekly outputs
* Sources: `d:15`, `v:15.2`
