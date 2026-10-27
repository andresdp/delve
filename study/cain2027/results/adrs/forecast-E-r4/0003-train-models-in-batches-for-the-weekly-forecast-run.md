# Train models in batches for the weekly forecast run

* System: Retail demand forecasting

## Context and Problem Statement

The brief describes weekly forecasts and a small team owning the pipeline end to end. The design space contrasts batch, incremental, and hybrid learning (d:19).

## Decision Drivers

* Weekly cadence
* Small team

## Considered Options

* Batch-based learning (`v:19.1`)
* Incremental learning (`v:19.2`)
* Hybrid batch-based and incremental learning (`v:19.3`)

## Decision Outcome

Chosen option: "Batch-based learning" (`v:19.1`).

Batch training aligns with the weekly run and keeps the pipeline simpler for a three-person team (d:19, v:19.1).

### Consequences

* Retrain on a scheduled batch cadence.
* Model updates arrive with a training run.

## Pros and Cons of the Options

### Batch-based learning

* Good, because Fits scheduled retraining
* Bad, because Updates between runs wait
* Sources: `d:19`, `v:19.1`

### Incremental learning

* Good, because Updates incrementally
* Bad, because Adds training-state complexity
* Sources: `d:19`, `v:19.2`

### Hybrid batch-based and incremental learning

* Good, because Combines update modes
* Bad, because More operational complexity
* Sources: `d:19`, `v:19.3`
