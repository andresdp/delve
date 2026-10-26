# Batch-based learning

*When and how to train*

* System: Retail demand forecasting

## Context and Problem Statement

Weekly forecasts imply a recurring run, while the team also wants new model ideas to reach production quickly. The brief does not require continuous learning.

## Decision Drivers

* 1. Protect weekly run
* 2. Fast model iteration
* 3. Small team

## Considered Options

* Batch-based learning (`v:19.1`)
* Incremental learning (`v:19.2`)
* Hybrid batch-based and incremental learning (`v:19.3`)

## Decision Outcome

Chosen option: "Batch-based learning" (`v:19.1`).

Protecting the weekly run decides the choice: batch training fits the stated cadence and keeps the workflow manageable. The trade-off is that model changes wait for a batch cycle.

### Consequences

* Run training on a schedule aligned with the weekly forecast.
* The brief leaves the training-data cutoff and retraining cadence unspecified.

## Pros and Cons of the Options

### Batch-based learning

* Good, because Weekly run: fits scheduled offline training
* Bad, because Fast iteration: changes wait for a batch run
* Sources: `d:19`, `v:19.1`

### Incremental learning

* Good, because Fast iteration: can incorporate data incrementally
* Bad, because Weekly run: adds complexity to a simple recurring process
* Sources: `d:19`, `v:19.2`

### Hybrid batch-based and incremental learning

* Good, because Fast iteration: supports incremental updates
* Bad, because Small team: more training paths to maintain
* Sources: `d:19`, `v:19.3`
