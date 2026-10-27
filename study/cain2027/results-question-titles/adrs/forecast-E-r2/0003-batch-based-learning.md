# Batch-based learning

*How should training be scheduled?*

* System: Retail demand forecasting

## Context and Problem Statement

Forecasting runs weekly, while the brief asks for reproducibility of any past week. Batch training supports versioned training runs tied to retained data. [d:19, v:19.1]

## Decision Drivers

* Weekly cadence
* Past-week reproducibility

## Considered Options

* Batch-based learning (`v:19.1`)
* Incremental learning (`v:19.2`)
* Hybrid batch-based and incremental learning (`v:19.3`)

## Decision Outcome

Chosen option: "Batch-based learning" (`v:19.1`).

Offline batch training fits the weekly workflow and simplifies rerunning training from a specific historical data version. [d:19, v:19.1]

### Consequences

* Training occurs on a scheduled batch.
* Each run must record its data and model inputs.

## Pros and Cons of the Options

### Batch-based learning

* Good, because Repeatable offline runs
* Good, because Fits weekly cadence
* Bad, because Model refresh waits for batch
* Sources: `d:19`, `v:19.1`

### Incremental learning

* Good, because Updates as data arrives
* Bad, because Harder to reconstruct prior state
* Sources: `d:19`, `v:19.2`

### Hybrid batch-based and incremental learning

* Good, because Combines batch and incremental updates
* Bad, because More complex model state
* Sources: `d:19`, `v:19.3`
