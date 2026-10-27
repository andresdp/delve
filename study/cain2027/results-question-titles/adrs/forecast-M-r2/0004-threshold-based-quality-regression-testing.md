# Threshold-based quality regression testing

*How should candidate forecasts be evaluated?*

* System: Retail demand forecasting

## Context and Problem Statement

Model changes need validation before they affect the weekly production run. Historical data provides a basis for offline evaluation and regression checks.

## Decision Drivers

* Avoid quality regressions
* Compare model ideas
* Protect weekly forecasts

## Considered Options

* Threshold-based quality regression testing (`v:13.2`)
* Offline evaluation pipeline (`v:13.1`)

## Decision Outcome

Chosen option: "Threshold-based quality regression testing" (`v:13.2`).

Threshold checks directly address the risk of a model update degrading weekly forecast quality, and can be run before promotion. Google’s MLOps guidance and MLOps Principles support threshold-based regression checks; the checked design point warns that workflow coordination must be decided first.

### Consequences

* Choose and maintain forecast quality thresholds.
* Historical evaluation data and metric definitions are required.

## Pros and Cons of the Options

### Threshold-based quality regression testing

* Good, because Catches quality drops
* Good, because Checks changes against thresholds
* Bad, because Thresholds require calibration
* Sources: `s06_p02`, `s06_p08`, `s09_p07`, `s22_p09`

### Offline evaluation pipeline

* Good, because Tests candidates before release
* Good, because Uses held-out data
* Bad, because Needs evaluation data and metrics
* Sources: `s02_p09`, `s04_p15`, `s06_p08`, `s08_p02`
