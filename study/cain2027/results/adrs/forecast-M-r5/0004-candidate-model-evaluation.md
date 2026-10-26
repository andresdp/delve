# Candidate model evaluation

* System: Retail demand forecasting

## Context and Problem Statement

New forecasting ideas must reach production quickly without disrupting the weekly run. Candidate models need a repeatable pre-promotion quality check.

## Decision Drivers

* Safe model changes
* Fast iteration
* Forecast quality

## Considered Options

* Offline evaluation pipeline (`v:13.1`)
* Previously-built-model diff testing (`v:13.3`)

## Decision Outcome

Chosen option: "Offline evaluation pipeline" (`v:13.1`).

Offline checks let candidates be assessed before the production weekly run, which best addresses safe iteration. “MLOps: Continuous delivery and automation pipelines in machine learning” and “MLOps Principles” describe evaluation as part of the production pipeline; the checked point has no warnings but is unattested.

### Consequences

* Define forecast metrics and promotion thresholds.
* Keep evaluation data separate from training and tuning.

## Pros and Cons of the Options

### Offline evaluation pipeline

* Good, because Checks before promotion
* Good, because Uses held-out data
* Bad, because Needs trusted labels
* Bad, because Evaluation adds pipeline work
* Sources: `s02_p09`, `s04_p15`, `s06_p08`, `s08_p02`, `s09_p04`, `s20_p03`, `s20_p09`, `s22_p08`, `s25_p09`

### Previously-built-model diff testing

* Good, because Direct version comparison
* Good, because Can expose changes
* Bad, because Maintenance burden
* Bad, because Mixed source support
