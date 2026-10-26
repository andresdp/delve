# Offline evaluation pipeline

*How should candidate models be evaluated?*

* System: On-device visual inspection

## Context and Problem Statement

Weekly retraining creates frequent candidate models that need a consistent promotion check. The design space includes offline evaluation against held-out data and metric-driven candidate comparison.

## Decision Drivers

* Safe weekly updates
* Reproducibility
* Small team

## Considered Options

* Offline evaluation pipeline (`v:13.1`)
* Metric-driven candidate model evaluation (`v:13.6`)
* Threshold-based quality regression testing (`v:13.2`)

## Decision Outcome

Chosen option: "Offline evaluation pipeline" (`v:13.1`).

Safe weekly updates decide the choice: evaluate candidates against held-out labelled data before promotion, accepting the work of maintaining that evaluation set. “MLOps: Continuous delivery and automation pipelines in machine learning” and “MLOps Principles” describe offline candidate validation and quality checks.

### Consequences

* Preserve a held-out labelled set for comparison.
* Set promotion criteria before automating device rollout.

## Pros and Cons of the Options

### Offline evaluation pipeline

* Good, because Safe weekly updates: checks candidates before deployment
* Bad, because Small team: requires held-out data and evaluation upkeep
* Sources: `s02_p09`, `s06_p08`

### Metric-driven candidate model evaluation

* Good, because Small team: focused comparison on chosen metrics
* Bad, because Safe weekly updates: metric choice can miss other regressions

### Threshold-based quality regression testing

* Good, because Safe weekly updates: blocks quality drops
* Bad, because Reproducibility: thresholds need stable definitions
* Sources: `s06_p08`, `s22_p09`
