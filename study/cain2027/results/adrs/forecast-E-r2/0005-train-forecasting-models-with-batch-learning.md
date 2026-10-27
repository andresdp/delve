# Train forecasting models with batch learning

* System: Retail demand forecasting

## Context and Problem Statement

The brief describes weekly forecasts and reproducibility for past weeks, with no requirement for online updates. Batch learning aligns training with versioned historical inputs (d:19).

## Decision Drivers

* Weekly cadence
* Historical reproducibility
* Three-person team

## Considered Options

* Batch-based learning (`v:19.1`)
* Incremental learning (`v:19.2`)
* Hybrid batch-based and incremental learning (`v:19.3`)

## Decision Outcome

Chosen option: "Batch-based learning" (`v:19.1`).

Batch learning supports controlled, reproducible retraining on historical data and fits the weekly operating rhythm (d:19, v:19.1).

### Consequences

* Track training data and model versions per run.
* Model changes reach production through the release process.

## Pros and Cons of the Options

### Batch-based learning

* Good, because Repeatable training runs
* Good, because Fits scheduled workflow
* Bad, because Model updates wait for retraining
* Bad, because Requires batch compute
* Sources: `d:19`, `v:19.1`

### Incremental learning

* Good, because Adapts with incoming data
* Good, because Can reduce full retraining
* Bad, because Harder to reproduce state
* Bad, because Adds update complexity
* Sources: `d:19`, `v:19.2`

### Hybrid batch-based and incremental learning

* Good, because Combines periodic and incremental updates
* Good, because Flexible adaptation
* Bad, because More complex state management
* Bad, because Harder to operate with a small team
* Sources: `d:19`, `v:19.3`
