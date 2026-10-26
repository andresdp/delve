# How should weekly training candidates be evaluated?

* System: On-device visual inspection

## Context and Problem Statement

Newly labeled images feed a weekly retraining cycle. A candidate needs validation before it replaces the deployed model.

## Decision Drivers

* Weekly retraining
* Regression control

## Considered Options

* Offline evaluation pipeline (`v:13.1`)
* Metric-driven candidate model evaluation (`v:13.6`)

## Decision Outcome

Chosen option: "Offline evaluation pipeline" (`v:13.1`).

Evaluate each weekly candidate offline against held-out examples before selection. “MLOps: Continuous delivery and automation pipelines in machine learning” and “MLOps Principles” support evaluation and regression thresholds; both checked combinations warned that workflow coordination must be decided first.

### Consequences

* Maintain held-out labeled inspection examples.
* Set acceptance thresholds before promotion.

## Pros and Cons of the Options

### Offline evaluation pipeline

* Good, because Checks against held-out data
* Good, because Supports pre-deployment selection
* Bad, because Requires representative test data
* Bad, because Adds promotion time
* Sources: `s02_p09`, `s06_p08`, `s22_p09`

### Metric-driven candidate model evaluation

* Good, because Compares candidate models
* Good, because Uses selected metrics
* Bad, because Metric choice matters
* Bad, because Does not alone ensure safe rollout
* Sources: `s20_p03`, `s20_p09`
