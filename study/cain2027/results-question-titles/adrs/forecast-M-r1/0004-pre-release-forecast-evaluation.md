# Pre-release forecast evaluation

* System: Retail demand forecasting

## Context and Problem Statement

Candidates need to be evaluated before replacing the production model, with checks that detect deterioration. The brief does not specify a particular forecasting metric or threshold.

## Decision Drivers

* Avoid regressions
* Compare model ideas
* Protect weekly run

## Considered Options

* Offline evaluation pipeline (`v:13.1`)
* Threshold-based quality regression testing (`v:13.2`)

## Decision Outcome

Chosen option: "Offline evaluation pipeline" (`v:13.1`).

Offline evaluation provides the pre-promotion comparison needed to introduce new model ideas safely. “MLOps Principles” and “MLOps: Continuous delivery and automation pipelines in machine learning” support held-out evaluation; metric and threshold selection remain system-specific.

### Consequences

* Evaluate candidates before promotion.
* Preserve evaluation data and results for comparison.
* Define forecasting metrics and acceptance thresholds separately.

## Pros and Cons of the Options

### Offline evaluation pipeline

* Good, because Tests candidates before deployment
* Good, because Uses held-out data
* Bad, because Depends on suitable labels
* Bad, because Does not set business thresholds
* Sources: `s02_p09`, `s04_p15`, `s06_p08`, `s08_p02`, `s09_p04`, `s20_p03`, `s20_p09`, `s22_p08`, `s25_p09`

### Threshold-based quality regression testing

* Good, because Flags quality drops
* Good, because Can gate promotion
* Bad, because Requires chosen thresholds
* Bad, because Needs ongoing calibration
* Sources: `s06_p02`, `s06_p08`, `s09_p07`, `s22_p09`, `s24_p07`, `s24_p08`
