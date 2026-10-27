# Evaluate candidate forecasts offline before promotion

* System: Retail demand forecasting

## Context and Problem Statement

Model changes need evidence of quality before they reach the recurring production run. The brief does not specify a forecasting metric, so that choice remains open.

## Decision Drivers

* Avoid regressions
* Safe model updates

## Considered Options

* Offline evaluation pipeline (`v:13.1`)
* Threshold-based quality regression testing (`v:13.2`)

## Decision Outcome

Chosen option: "Offline evaluation pipeline" (`v:13.1`).

Offline candidate evaluation provides a promotion check before production; threshold checks can complement it once the retailer defines appropriate measures. MLOps: Continuous delivery and automation pipelines in machine learning and MLOps Principles support offline evaluation. The point check warned that this decision depends on first deciding workflow coordination.

### Consequences

* Define representative historical evaluation data.
* Choose forecasting measures and promotion thresholds.

## Pros and Cons of the Options

### Offline evaluation pipeline

* Good, because Checks candidates before release
* Good, because Uses held-out data
* Bad, because Needs representative evaluation data
* Sources: `s02_p09`, `s04_p15`, `s06_p08`, `s08_p02`, `s09_p04`, `s20_p03`, `s20_p09`, `s22_p08`, `s25_p09`

### Threshold-based quality regression testing

* Good, because Catches quality drops
* Good, because Can gate promotion
* Bad, because Requires chosen thresholds
* Sources: `s06_p02`, `s06_p08`, `s09_p07`, `s22_p09`, `s24_p07`, `s24_p08`
