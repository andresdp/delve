# Evaluate candidates offline before promotion

* System: Retail demand forecasting

## Context and Problem Statement

Model changes must not break forecasts already used by the weekly run. Candidate quality needs assessment before a release reaches production.

## Decision Drivers

* Protect forecast quality
* Safe model iteration
* Repeatable weekly process

## Considered Options

* Offline evaluation pipeline (`v:13.1`)
* Metric-driven candidate model evaluation (`v:13.6`)

## Decision Outcome

Chosen option: "Offline evaluation pipeline" (`v:13.1`).

Choose held-out offline evaluation as a pre-release quality gate, with the pipeline running it consistently before model promotion. “MLOps Principles” and “MLOps: Continuous delivery and automation pipelines in machine learning” describe offline evaluation in the delivery workflow.

### Consequences

* Evaluation data and criteria need versioning.
* Promotion depends on evaluation results.

## Pros and Cons of the Options

### Offline evaluation pipeline

* Good, because Checks held-out data
* Good, because Fits staged promotion
* Bad, because Needs representative test data
* Bad, because Does not prove live performance
* Sources: `s02_p09`, `s04_p15`, `s06_p08`, `s08_p02`, `s09_p04`, `s20_p03`, `s22_p08`, `s25_p09`

### Metric-driven candidate model evaluation

* Good, because Compares candidate metrics
* Good, because Supports model selection
* Bad, because Metric choice matters
* Bad, because May miss data leakage
* Sources: `s02_p09`, `s09_p04`, `s09_p07`, `s09_p09`, `s22_p06`, `s22_p15`, `s25_p09`
