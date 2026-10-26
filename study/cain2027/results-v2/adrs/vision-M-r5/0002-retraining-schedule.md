# Retraining schedule

* System: On-device visual inspection

## Context and Problem Statement

The model is retrained weekly from newly labelled images. The system needs to start training on that cadence.

## Decision Drivers

* Weekly retraining
* Small-team operations

## Considered Options

* Schedule-based retraining trigger (`v:6.6`)
* Manual retraining trigger (`v:6.14`)

## Decision Outcome

Chosen option: "Schedule-based retraining trigger" (`v:6.6`).

Weekly retraining decides the choice: a schedule starts training consistently without relying on a person to remember each run. “Architecting a Machine Learning Pipeline” and “MLOps: Continuous delivery and automation pipelines in machine learning” document recurring retraining schedules.

### Consequences

* The weekly job must have access to newly labelled images.
* Failed runs need a way to be noticed and retried.

## Pros and Cons of the Options

### Schedule-based retraining trigger

* Good, because Weekly retraining: matches recurring cadence
* Bad, because Small-team operations: schedule needs oversight
* Sources: `s02_p08`, `s06_p11`

### Manual retraining trigger

* Good, because Small-team operations: simple to start
* Bad, because Weekly retraining: depends on a person each week
