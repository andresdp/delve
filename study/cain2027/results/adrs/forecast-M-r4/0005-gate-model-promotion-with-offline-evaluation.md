# Gate model promotion with offline evaluation

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas need a consistent comparison before they can affect scheduled forecasts. Historical demand and held-out actuals enable evaluation before promotion.

## Decision Drivers

* Model comparison
* Avoid regressions

## Considered Options

* Offline evaluation pipeline (`v:13.1`)
* Threshold-based quality regression testing (`v:13.2`)

## Decision Outcome

Chosen option: "Offline evaluation pipeline" (`v:13.1`).

Offline evaluation enables candidate selection against held-out actuals before scheduled prediction; “MLOps: Continuous delivery and automation pipelines in machine learning” and “MLOps Principles” describe evaluation before deployment (s06_p08, s22_p08).

### Consequences

* Promotion waits for evaluation data and results.

## Pros and Cons of the Options

### Offline evaluation pipeline

* Good, because Tests against held-out data
* Good, because Supports candidate selection
* Bad, because Depends on available actuals
* Sources: `s02_p09`, `s04_p15`, `s06_p08`, `s08_p02`, `s09_p04`, `s20_p03`, `s20_p09`, `s22_p08`, `s25_p09`

### Threshold-based quality regression testing

* Good, because Flags quality drops
* Good, because Can block promotion
* Bad, because Requires agreed thresholds
* Sources: `s06_p02`, `s06_p08`, `s09_p07`, `s22_p09`, `s24_p07`, `s24_p08`
