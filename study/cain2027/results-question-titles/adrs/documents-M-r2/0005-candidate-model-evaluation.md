# Candidate model evaluation

* System: Large-scale document classification

## Context and Problem Statement

Drift response may lead to model updates, and candidate classifiers need a quality check before deployment. The brief does not define an evaluation metric or acceptance threshold.

## Decision Drivers

* Classification quality
* Safe updates
* Regression control

## Considered Options

* Offline evaluation pipeline (`v:13.1`)
* Metric-driven candidate model evaluation (`v:13.6`)

## Decision Outcome

Chosen option: "Offline evaluation pipeline" (`v:13.1`).

Held-out offline evaluation gives a pre-deployment quality gate for any update. “Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2” documents candidate evaluation; the point check flagged that workflow coordination should be decided first, and its combination was unattested.

### Consequences

* Model promotion waits for evaluation.
* The brief must define labels, metrics, and acceptance thresholds.

## Pros and Cons of the Options

### Offline evaluation pipeline

* Good, because Tests held-out examples
* Good, because Checks candidates before deployment
* Bad, because Needs representative labeled data
* Sources: `s02_p09`

### Metric-driven candidate model evaluation

* Good, because Compares candidate models
* Good, because Makes selection measurable
* Bad, because Requires metric selection
* Sources: `s02_p09`
