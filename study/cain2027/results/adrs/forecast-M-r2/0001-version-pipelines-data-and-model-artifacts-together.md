# Version pipelines, data, and model artifacts together

* System: Retail demand forecasting

## Context and Problem Statement

Forecasts must be reproducible for any past week, which requires retaining the inputs and workflow context behind each result.

## Decision Drivers

* Past-week reproducibility
* Traceable runs

## Considered Options

* Pipeline and experiment version control (`v:20.2`)
* Comprehensive ML lifecycle traceability (`v:20.3`)

## Decision Outcome

Chosen option: "Comprehensive ML lifecycle traceability" (`v:20.3`).

It connects datasets, pipeline definitions, training runs, and artifacts, which best supports reproducing a forecast for a past week. MLOps Principles and Continuous Intelligence describe this integrated lifecycle approach.

### Consequences

* Record dataset versions and run metadata.
* Retain versioned pipeline and model artifacts.

## Pros and Cons of the Options

### Pipeline and experiment version control

* Good, because Versions pipelines and experiments
* Good, because Supports comparison and replay
* Bad, because Limited lifecycle coverage
* Sources: `s04_p01`, `s04_p03`, `s04_p05`

### Comprehensive ML lifecycle traceability

* Good, because Links datasets, runs, and artifacts
* Good, because Supports end-to-end traceability
* Bad, because More metadata to maintain
* Sources: `s08_p01`, `s08_p02`, `s22_p03`, `s22_p04`
