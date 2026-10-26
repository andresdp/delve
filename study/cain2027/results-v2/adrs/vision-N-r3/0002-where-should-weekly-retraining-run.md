# Where should weekly retraining run?

* System: On-device visual inspection

## Context and Problem Statement

The model is retrained weekly from newly labelled images, while the device fleet may be offline and the team and infrastructure budget are small.

## Decision Drivers

* Reproducibility
* Low cost
* Weekly freshness

## Considered Options

* Central training pipeline
* Train on production devices
* Manual training on a team workstation

## Decision Outcome

Chosen option: "Central training pipeline".

Reproducibility decides the choice: a controlled shared pipeline makes weekly model builds repeatable. This gives up some operational simplicity because the team must maintain the pipeline.

### Consequences

* Keep training inputs and configuration with each model build.
* Reserve shared compute for the weekly training run.

## Pros and Cons of the Options

### Central training pipeline

* Good, because Reproducibility: controlled training environment
* Good, because Low cost: shared compute
* Bad, because Weekly freshness: pipeline needs operational upkeep

### Train on production devices

* Good, because Low cost: reuses device compute
* Bad, because Reproducibility: varied device conditions
* Bad, because Weekly freshness: competes with inspection workload

### Manual training on a team workstation

* Good, because Low cost: avoids dedicated infrastructure
* Bad, because Reproducibility: manual steps vary
* Bad, because Weekly freshness: depends on team availability
