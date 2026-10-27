# Retrain models weekly from newly labelled images

* System: On-device visual inspection

## Context and Problem Statement

Newly labelled images are available each week, and the model is retrained on that cadence. The brief does not specify how training compute is hosted.

## Decision Drivers

* Weekly retraining
* New labelled images
* Tight infrastructure budget

## Considered Options

* Scheduled shared training pipeline
* Manual retraining by an engineer

## Decision Outcome

Chosen option: "Scheduled shared training pipeline".

A scheduled pipeline supports the specified weekly cadence while sharing limited training infrastructure.

### Consequences

* Training inputs and outputs need tracking
* Pipeline failures can delay a release

## Pros and Cons of the Options

### Scheduled shared training pipeline

* Good, because Repeatable weekly runs
* Good, because Shared compute
* Bad, because Pipeline upkeep

### Manual retraining by an engineer

* Good, because Simple initial setup
* Bad, because Manual effort
* Bad, because Harder to reproduce
