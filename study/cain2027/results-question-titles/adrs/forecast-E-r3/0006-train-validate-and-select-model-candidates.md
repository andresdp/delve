# Train, validate, and select model candidates

*What should the model building pipeline do?*

* System: Retail demand forecasting

## Context and Problem Statement

Model experimentation should feed production through a consistent evaluation path. The pipeline can train candidates and validate them before promotion.

## Decision Drivers

* Fast iteration
* Protect weekly run
* Reproducible selection

## Considered Options

* Train, validate, and select model candidates
* Model training only (`v:20.1`)
* Model hyperparameter tuning (`v:20.10`)

## Decision Outcome

Chosen option: "Train, validate, and select model candidates".

Training, validation, and model selection give new ideas a repeatable route to production while separating candidate evaluation from the weekly forecast run (d:20, v:20.1, v:20.4, v:20.5).

### Consequences

* Candidate runs need comparable evaluation data.
* Selection criteria must be maintained.

## Pros and Cons of the Options

### Train, validate, and select model candidates

* Good, because Compares candidate models
* Good, because Automates quality gates
* Bad, because More compute per run
* Sources: `d:20`, `v:20.1`, `v:20.4`, `v:20.5`, `v:20.9`

### Model training only

* Good, because Simple pipeline
* Bad, because Selection remains manual
* Sources: `d:20`, `v:20.1`

### Model hyperparameter tuning

* Good, because Explores configurations
* Bad, because Can expand run time
* Sources: `d:20`, `v:20.10`
