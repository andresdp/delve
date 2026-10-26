# How should weekly demand data be processed?

* System: Retail demand forecasting

## Context and Problem Statement

The retailer publishes forecasts weekly per store and product. Batch processing aligns the workflow with that cadence. [d:15]

## Decision Drivers

* Weekly forecast cadence
* Reproducibility

## Considered Options

* Batch-based data processing (`v:15.1`)
* Real-time, stream-based data processing (`v:15.2`)

## Decision Outcome

Chosen option: "Batch-based data processing" (`v:15.1`).

A weekly batch run matches the stated forecast cadence and allows the team to rerun a past week against versioned inputs. [d:15, v:15.1]

### Consequences

* Forecasts update on the scheduled run.
* Historical runs need their input versions retained.

## Pros and Cons of the Options

### Batch-based data processing

* Good, because Fits weekly runs
* Good, because Supports historical reruns
* Bad, because Forecasts refresh on batch cadence
* Sources: `d:15`, `v:15.1`

### Real-time, stream-based data processing

* Good, because Continuous updates
* Bad, because Adds streaming complexity
* Sources: `d:15`, `v:15.2`
