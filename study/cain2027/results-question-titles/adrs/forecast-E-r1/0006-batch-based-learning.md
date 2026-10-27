# Batch-based learning

*When should models be trained?*

* System: Retail demand forecasting

## Context and Problem Statement

Forecasts are weekly and past results must be reproducible; the brief does not call for online updates.

## Decision Drivers

* Weekly cadence
* Reproducibility

## Considered Options

* Batch-based learning (`v:19.1`)
* Incremental learning (`v:19.2`)

## Decision Outcome

Chosen option: "Batch-based learning" (`v:19.1`).

Batch training aligns model updates with the weekly workflow and supports repeatable training runs (d:19, v:19.1).

### Consequences

* New training data is incorporated on a batch cadence.
* Each training run must be tied to its input versions.

## Pros and Cons of the Options

### Batch-based learning

* Good, because Repeatable training runs
* Good, because Fits weekly cadence
* Bad, because Model updates wait for a run
* Sources: `d:19`, `v:19.1`

### Incremental learning

* Good, because Frequent model updates
* Bad, because Harder to reproduce training state
* Sources: `d:19`, `v:19.2`
