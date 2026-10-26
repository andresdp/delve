# When and how should the model be trained?

* System: Retail demand forecasting

## Context and Problem Statement

The brief requires weekly forecasts and fast delivery of new model ideas. It does not require adapting the model continuously between forecast runs.

## Decision Drivers

* Weekly cadence
* Fast model iteration
* Reproducibility

## Considered Options

* Batch-based learning (`v:19.1`)
* Incremental learning (`v:19.2`)
* Hybrid batch-based and incremental learning (`v:19.3`)

## Decision Outcome

Chosen option: "Batch-based learning" (`v:19.1`).

Batch training aligns with weekly forecasting and supports repeatable runs. The checked design point has no warnings, but is unattested.

### Consequences

* Train from versioned inputs on a schedule.
* Record the code and model version for each run.

## Pros and Cons of the Options

### Batch-based learning

* Good, because Repeatable training runs
* Good, because Fits scheduled workflow
* Bad, because Updates wait for next run
* Sources: `d:19`, `v:19.1`

### Incremental learning

* Good, because Updates incrementally
* Bad, because More state to reproduce
* Sources: `d:19`, `v:19.2`

### Hybrid batch-based and incremental learning

* Good, because Combines batch and incremental updates
* Bad, because More moving parts
* Sources: `d:19`, `v:19.3`
