# Track complete ML lifecycle state for reproducible forecasts

* System: Retail demand forecasting

## Context and Problem Statement

Reproducing any past week requires retaining the data, pipeline, dependencies, and training run context behind a forecast.

## Decision Drivers

* Past-week reproducibility
* Traceable runs

## Considered Options

* End-to-end reproducible lifecycle governance (`v:20.6`)
* Artifact version control (`v:20.1`)

## Decision Outcome

Chosen option: "End-to-end reproducible lifecycle governance" (`v:20.6`).

Its broader lineage includes dataset versions and training snapshots, which better supports reconstructing a forecast for a past week. MLOps: What It Is, Why it Matters, and How To Implement It (from a Data Scientist Perspective) and MLOps: Model management, deployment, and monitoring with Azure Machine Learning support this approach.

### Consequences

* Retain dataset and run metadata alongside model artifacts.
* Replays depend on preserving source data and dependencies.

## Pros and Cons of the Options

### End-to-end reproducible lifecycle governance

* Good, because Covers datasets through deployment
* Good, because Supports run reconstruction
* Bad, because Adds metadata and governance work
* Sources: `s21_p03`, `s21_p05`, `s21_p06`, `s21_p09`, `s21_p10`, `s21_p17`, `s21_p18`, `s25_p01`, `s25_p02`, `s25_p07`

### Artifact version control

* Good, because Versions models and dependencies
* Good, because Supports repeatable deployment
* Bad, because Less complete run context
* Sources: `s21_p03`, `s25_p01`
