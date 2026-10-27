# Process weekly demand data in batches

* System: Retail demand forecasting

## Context and Problem Statement

The brief specifies weekly forecasts per store and product, with no real-time requirement. Batch processing fits the stated cadence (d:15).

## Decision Drivers

* Weekly cadence
* Small team

## Considered Options

* Batch-based data processing (`v:15.1`)
* Real-time, stream-based data processing (`v:15.2`)

## Decision Outcome

Chosen option: "Batch-based data processing" (`v:15.1`).

Weekly batch processing matches the brief’s forecast cadence and avoids introducing streaming operations without a stated need (d:15, v:15.1). The checked point had no warnings; it was unattested, as was the streaming rival.

### Consequences

* Forecasts refresh on the weekly schedule.
* Late-arriving data needs an explicit rerun policy.

## Pros and Cons of the Options

### Batch-based data processing

* Good, because Matches weekly runs
* Good, because Straightforward replay
* Bad, because Results arrive on schedule
* Bad, because No immediate updates
* Sources: `d:15`, `v:15.1`

### Real-time, stream-based data processing

* Good, because Processes events continuously
* Good, because Supports low-latency updates
* Bad, because More operational complexity
* Bad, because Exceeds stated cadence
* Sources: `d:15`, `v:15.2`
