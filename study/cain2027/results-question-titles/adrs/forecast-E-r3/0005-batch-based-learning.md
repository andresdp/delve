# Batch-based learning

*How should training fit the workflow?*

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas need a path to production that does not disrupt the weekly forecast run. Training can remain an offline, repeatable step.

## Decision Drivers

* Weekly run stability
* Reproducibility
* Fast model iteration

## Considered Options

* Batch-based learning (`v:19.1`)
* Incremental learning (`v:19.2`)
* Hybrid batch-based and incremental learning (`v:19.3`)

## Decision Outcome

Chosen option: "Batch-based learning" (`v:19.1`).

Batch training keeps model creation repeatable and aligned with the weekly workflow (d:19, v:19.1).

### Consequences

* Training happens on a defined dataset snapshot.
* Model updates wait for the next training run.

## Pros and Cons of the Options

### Batch-based learning

* Good, because Repeatable training runs
* Good, because Fits weekly cadence
* Bad, because No immediate adaptation
* Sources: `d:19`, `v:19.1`

### Incremental learning

* Good, because Adapts continuously
* Bad, because More state to reproduce
* Sources: `d:19`, `v:19.2`

### Hybrid batch-based and incremental learning

* Good, because Combines update styles
* Bad, because More complex workflow
* Sources: `d:19`, `v:19.3`
