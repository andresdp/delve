# Training compute scaling

* System: On-device visual inspection

## Context and Problem Statement

The model is retrained every week, and infrastructure budget is tight. No training duration or data-volume limit is specified.

## Decision Drivers

* Low infrastructure cost
* Weekly retraining

## Considered Options

* Vertically scalable training (`v:3.1`)
* Parallel candidate training (`v:3.5`)

## Decision Outcome

Chosen option: "Vertically scalable training" (`v:3.1`).

Low infrastructure cost decides the choice: scale on a single larger machine until training duration or capacity requires more, giving up parallel candidate speed. “System Architectures for Personalization and Recommendation” describes vertical scaling, while “MLOps: Methods and Tools of DevOps for Machine Learning” describes parallel candidate training.

### Consequences

* A single machine limits training capacity.
* The brief lacks data-volume and training-time targets to set a scaling threshold.

## Pros and Cons of the Options

### Vertically scalable training

* Good, because Low infrastructure cost: avoids distributed setup
* Bad, because Weekly retraining: limited by one machine’s capacity
* Sources: `s11_p06`, `s12_p03`

### Parallel candidate training

* Good, because Weekly retraining: compares candidates concurrently
* Bad, because Low infrastructure cost: uses more compute
* Sources: `s02_p05`, `s20_p09`
