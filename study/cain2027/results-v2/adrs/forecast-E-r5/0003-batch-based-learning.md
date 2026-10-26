# Batch-based learning

*When and how to train the model?*

* System: Retail demand forecasting

## Context and Problem Statement

The team needs to bring model ideas into production quickly while maintaining reproducible forecasts. The brief does not describe online learning needs.

## Decision Drivers

* Reproducibility
* Fast iteration
* Weekly run

## Considered Options

* Batch-based learning (`v:19.1`)
* Incremental learning (`v:19.2`)
* Hybrid batch-based and incremental learning (`v:19.3`)

## Decision Outcome

Chosen option: "Batch-based learning" (`v:19.1`).

Reproducibility decides the choice: batch training can be tied to a fixed data version and run. The trade-off is that new ideas wait for a training cycle before evaluation and release.

### Consequences

* Train from versioned weekly data snapshots.
* Record the training inputs and resulting model version.

## Pros and Cons of the Options

### Batch-based learning

* Good, because Reproducibility: training can use fixed inputs
* Good, because Weekly run: fits periodic training
* Bad, because Fast iteration: model updates await a training run
* Sources: `d:19`, `v:19.1`

### Incremental learning

* Good, because Fast iteration: updates can be applied incrementally
* Bad, because Reproducibility: evolving model state complicates replay
* Sources: `d:19`, `v:19.2`

### Hybrid batch-based and incremental learning

* Good, because Fast iteration: supports incremental updates
* Bad, because Reproducibility: more moving model state
* Bad, because Weekly run: adds operational complexity
* Sources: `d:19`, `v:19.3`
