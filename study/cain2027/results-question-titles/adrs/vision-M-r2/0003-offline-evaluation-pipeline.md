# Offline evaluation pipeline

*How should candidate models be evaluated?*

* System: On-device visual inspection

## Context and Problem Statement

Weekly training produces updated candidates that must be assessed before they replace models on production devices.

## Decision Drivers

* Weekly model updates
* Production quality

## Considered Options

* Offline evaluation pipeline (`v:13.1`)
* Metric-driven candidate model evaluation (`v:13.6`)

## Decision Outcome

Chosen option: "Offline evaluation pipeline" (`v:13.1`).

Evaluate each candidate against held-out labelled images before selecting it for rollout. “MLOps: Continuous delivery and automation pipelines in machine learning” and “Architecting a Machine Learning Pipeline” describe offline evaluation before deployment (s06_p08, s02_p09).

### Consequences

* Maintain held-out labelled images.
* Block promotion when evaluation fails.

## Pros and Cons of the Options

### Offline evaluation pipeline

* Good, because Tests against held-out data
* Good, because Fits pre-release review
* Bad, because Requires representative test data
* Sources: `s02_p09`, `s06_p08`, `s20_p03`

### Metric-driven candidate model evaluation

* Good, because Compares candidates by metric
* Good, because Supports selection
* Bad, because Metric choice affects results
* Sources: `s09_p04`, `s19_p05`, `s22_p06`
