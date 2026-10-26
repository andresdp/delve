# End-to-end reproducible lifecycle governance

*How should historical forecasts be reproducible?*

* System: Retail demand forecasting

## Context and Problem Statement

Recreating a forecast for a past week requires the team to recover the relevant data and model context, not just the model artifact. The brief makes this a system requirement.

## Decision Drivers

* Historical reproducibility
* Weekly run safety
* Small team

## Considered Options

* End-to-end reproducible lifecycle governance (`v:20.6`)
* Artifact version control (`v:20.1`)

## Decision Outcome

Chosen option: "End-to-end reproducible lifecycle governance" (`v:20.6`).

Historical reproducibility decides: tracking dataset versions, pipeline definitions, dependencies, and run metadata supports reconstructing past forecasts. This costs metadata upkeep; “MLOps: What It Is, Why it Matters, and How To Implement It” and “MLOps: Model management, deployment, and monitoring with Azure Machine Learning” support lifecycle traceability.

### Consequences

* Each run needs linked data, code, configuration, and artifact versions.
* The team must preserve historical inputs and metadata.

## Pros and Cons of the Options

### End-to-end reproducible lifecycle governance

* Good, because Historical reproducibility: tracks datasets, runs, and artifacts
* Good, because Weekly run safety: preserves lifecycle context
* Bad, because Small team: metadata process needs upkeep
* Sources: `s21_p03`, `s21_p05`, `s21_p06`, `s21_p09`, `s21_p10`, `s21_p17`, `s21_p18`, `s25_p01`, `s25_p02`, `s25_p07`

### Artifact version control

* Good, because Small team: narrower tracking scope
* Bad, because Historical reproducibility: omits full data and run context
* Sources: ``
