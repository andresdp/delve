# Batch-based data processing

*How should weekly demand data be processed?*

* System: Retail demand forecasting

## Context and Problem Statement

The system forecasts weekly demand per store and product. A scheduled batch workflow fits the forecast interval.

## Decision Drivers

* Weekly forecasts
* Small team

## Considered Options

* Batch-based data processing (`v:15.1`)
* Real-time, stream-based data processing (`v:15.2`)

## Decision Outcome

Chosen option: "Batch-based data processing" (`v:15.1`).

Weekly demand forecasts do not require real-time processing. The checked design point has no warnings, though it is unattested in the design space.

### Consequences

* Run processing on a weekly schedule.
* Record each run's input period.

## Pros and Cons of the Options

### Batch-based data processing

* Good, because Fits weekly cadence
* Good, because Simple to reproduce
* Bad, because Not real time
* Sources: `d:15`, `v:15.1`

### Real-time, stream-based data processing

* Good, because Fresh as events arrive
* Bad, because More operational complexity
* Sources: `d:15`, `v:15.2`
