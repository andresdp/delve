# Evaluate candidate models offline before promotion

* System: Large-scale document classification

## Context and Problem Statement

Changes to the classifier need quality checks before deployment, especially when observed drift prompts model updates. The brief does not define the classification metrics or error costs.

## Decision Drivers

* Classification quality
* Safe model updates

## Considered Options

* Offline evaluation pipeline (`v:13.1`)
* Metric-driven candidate model evaluation (`v:13.6`)

## Decision Outcome

Chosen option: "Offline evaluation pipeline" (`v:13.1`).

Offline evaluation gives a pre-promotion quality gate for candidate models. The sources support the approach, but the checked combination had no attesting source.

### Consequences

* Maintain held-out labeled evaluation data.
* Choose claim-type metrics and thresholds.

## Pros and Cons of the Options

### Offline evaluation pipeline

* Good, because Uses held-out data
* Good, because Checks candidates before deployment
* Bad, because Needs representative labeled data
* Sources: `s02_p09`, `s04_p15`

### Metric-driven candidate model evaluation

* Good, because Compares candidates by metric
* Good, because Supports selection
* Bad, because Metric choice is unspecified
* Sources: `s09_p04`, `s22_p06`
