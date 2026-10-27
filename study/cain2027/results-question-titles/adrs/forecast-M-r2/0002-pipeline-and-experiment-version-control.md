# Pipeline and experiment version control

*How should past forecasts be reproducible?*

* System: Retail demand forecasting

## Context and Problem Statement

The brief requires reproducing forecasts for any past week. That requires retaining enough information about the data, pipeline, and experiment to reconstruct a run.

## Decision Drivers

* Past-week reproducibility
* Run traceability
* Experiment comparison

## Considered Options

* Pipeline and experiment version control (`v:20.2`)
* Artifact version control (`v:20.1`)

## Decision Outcome

Chosen option: "Pipeline and experiment version control" (`v:20.2`).

Versioning pipeline definitions and experiments alongside artifacts better serves reconstruction of a historical forecast than tracking artifacts alone. Productionizing Machine Learning with a Microservices Architecture and IBM’s AutoML overview support this approach.

### Consequences

* Record data and configuration references for each run.
* Retain the versioned assets needed to rebuild a forecast.

## Pros and Cons of the Options

### Pipeline and experiment version control

* Good, because Versions pipelines and experiments
* Good, because Supports run comparison
* Bad, because Requires consistent capture
* Sources: `s04_p01`, `s04_p03`, `s04_p05`, `s17_p03`

### Artifact version control

* Good, because Versions model artifacts
* Good, because Supports reuse
* Bad, because Does not track full run context
* Sources: `s12_p05`, `s19_p05`
