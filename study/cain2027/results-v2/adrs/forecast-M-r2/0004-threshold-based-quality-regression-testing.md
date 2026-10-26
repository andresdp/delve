# Threshold-based quality regression testing

*How should candidate models be checked before promotion?*

* System: Retail demand forecasting

## Context and Problem Statement

Quick model iteration still needs safeguards so a candidate does not damage the weekly forecast run. Evaluation thresholds provide a repeatable check against quality regression before promotion.

## Decision Drivers

* Weekly-run reliability
* Fast model iteration
* Past-week reproducibility

## Considered Options

* Threshold-based quality regression testing (`v:13.2`)
* Offline evaluation pipeline (`v:13.1`)

## Decision Outcome

Chosen option: "Threshold-based quality regression testing" (`v:13.2`).

Weekly-run reliability decides the choice: explicit quality thresholds can prevent a regressing candidate from promotion while keeping the check automatable. The cost is agreeing on and maintaining suitable thresholds; Google’s “MLOps: Continuous delivery and automation pipelines in machine learning” and “MLOps Principles” provide supporting evidence.

### Consequences

* Define forecast quality metrics and acceptable thresholds.
* Run regression checks before promotion.
* Review thresholds as forecasting needs change.

## Pros and Cons of the Options

### Threshold-based quality regression testing

* Good, because Reliability: blocks quality regressions
* Good, because Fast iteration: automated pass or fail
* Bad, because Team effort: define and maintain thresholds
* Sources: `s06_p02`, `s06_p08`, `s09_p07`, `s22_p09`

### Offline evaluation pipeline

* Good, because Reliability: checks candidates on held-out data
* Good, because Reproducibility: repeatable evaluation
* Bad, because Fast iteration: evaluation adds pipeline work
* Sources: `s02_p09`, `s04_p15`, `s06_p08`, `s09_p04`
