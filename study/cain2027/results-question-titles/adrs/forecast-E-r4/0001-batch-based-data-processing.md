# Batch-based data processing

*How should weekly inputs be processed?*

* System: Retail demand forecasting

## Context and Problem Statement

Demand is forecast weekly per store and product, so processing must align with the forecast cadence.

## Decision Drivers

* Weekly forecasts
* Small owning team

## Considered Options

* Batch-based data processing (`v:15.1`)
* Real-time, stream-based data processing (`v:15.2`)

## Decision Outcome

Chosen option: "Batch-based data processing" (`v:15.1`).

Weekly forecasts fit scheduled batch processing; the design point check produced no warnings, though no combinations are attested in this source-free space.

### Consequences

* Forecasts update on the weekly run.
* Late data waits for a later run or an explicit rerun.

## Pros and Cons of the Options

### Batch-based data processing

* Good, because Matches weekly cadence
* Good, because Supports reproducible runs
* Bad, because Results arrive on batch schedule
* Sources: `d:15`, `v:15.1`

### Real-time, stream-based data processing

* Good, because Processes events as they arrive
* Bad, because Adds streaming complexity
* Sources: `d:15`, `v:15.2`
