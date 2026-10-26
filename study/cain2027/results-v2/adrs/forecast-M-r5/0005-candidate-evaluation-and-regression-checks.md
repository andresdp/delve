# Candidate evaluation and regression checks

* System: Retail demand forecasting

## Context and Problem Statement

Model ideas need a repeatable quality gate before promotion so a new model does not degrade weekly forecasts. The brief does not specify a forecast error metric or acceptance threshold.

## Decision Drivers

* Protect weekly run
* Fast production changes

## Considered Options

* Threshold-based quality regression testing (`v:13.2`)
* Offline evaluation pipeline (`v:13.1`)

## Decision Outcome

Chosen option: "Threshold-based quality regression testing" (`v:13.2`).

Protecting the weekly run decides: explicit quality thresholds can block a degrading candidate, while the specific metric and threshold remain to be established. “MLOps: Continuous delivery and automation pipelines in machine learning” and “MLOps Principles” describe threshold-based checks; the checked point has no warnings but is unattested as a complete combination.

### Consequences

* Define forecast quality measures and promotion thresholds.
* Threshold changes require review as demand patterns change.

## Pros and Cons of the Options

### Threshold-based quality regression testing

* Good, because Weekly run: blocks threshold regressions
* Bad, because Fast production changes: thresholds need tuning
* Sources: `s06_p08`, `s09_p07`, `s22_p09`

### Offline evaluation pipeline

* Good, because Fast production changes: compares candidates before release
* Bad, because Weekly run: alone does not define regression limits
* Sources: `s02_p09`, `s06_p08`, `s09_p04`
