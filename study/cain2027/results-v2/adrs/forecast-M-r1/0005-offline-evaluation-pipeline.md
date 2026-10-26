# Offline evaluation pipeline

*How should candidate models be evaluated before promotion?*

* System: Retail demand forecasting

## Context and Problem Statement

The brief encourages new model ideas but requires the weekly run to remain dependable. Candidates need evaluation before they replace the current production model.

## Decision Drivers

* Weekly run safety
* Fast model iteration
* Historical reproducibility

## Considered Options

* Offline evaluation pipeline (`v:13.1`)
* Metric-driven candidate model evaluation (`v:13.6`)

## Decision Outcome

Chosen option: "Offline evaluation pipeline" (`v:13.1`).

Weekly run safety decides: evaluating candidates on held-out data before deployment helps prevent an unchecked model change from affecting production. This requires maintaining evaluation data; “Architecting a Machine Learning Pipeline” and “MLOps: Continuous delivery and automation pipelines in machine learning” describe evaluation before model selection or deployment.

### Consequences

* Held-out evaluation data and criteria must be maintained.
* Candidate evaluation becomes part of the release workflow.

## Pros and Cons of the Options

### Offline evaluation pipeline

* Good, because Weekly run safety: evaluates candidates before deployment
* Good, because Fast iteration: repeatable comparison against held-out data
* Bad, because Historical reproducibility: requires maintained evaluation data
* Sources: `s02_p09`, `s04_p15`, `s06_p08`, `s08_p02`, `s09_p04`, `s20_p03`, `s20_p09`, `s22_p08`, `s25_p09`

### Metric-driven candidate model evaluation

* Good, because Fast iteration: compares candidate models by metric
* Bad, because Weekly run safety: standalone metric comparison does not establish a release gate
* Sources: ``
