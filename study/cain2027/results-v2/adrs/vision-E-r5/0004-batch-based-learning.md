# Batch-based learning

*How should the model be trained?*

* System: On-device visual inspection

## Context and Problem Statement

The brief specifies weekly retraining from newly labelled images rather than continuous adaptation on the production device.

## Decision Drivers

* Weekly updates
* Reproducibility
* Tight budget

## Considered Options

* Batch-based learning (`v:19.1`)
* Incremental learning (`v:19.2`)

## Decision Outcome

Chosen option: "Batch-based learning" (`v:19.1`).

Reproducibility decides the choice: each weekly run can train from a fixed image set. This gives up incorporating labels immediately. The design space has no source passages; this choice is grounded in d:19 and v:19.1.

### Consequences

* Each run produces a discrete model artifact.
* Training can run away from production devices.
* Dataset selection must be recorded.

## Pros and Cons of the Options

### Batch-based learning

* Good, because Weekly updates: fits periodic retraining
* Good, because Reproducibility: trains from a fixed batch
* Bad, because Freshness: labels wait for the next run
* Sources: `d:19`, `v:19.1`

### Incremental learning

* Good, because Freshness: incorporates data incrementally
* Bad, because Reproducibility: model evolves across updates
* Bad, because Tight budget: may add operational complexity
* Sources: `d:19`, `v:19.2`
