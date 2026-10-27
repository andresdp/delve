# Reproducibility and lifecycle traceability

* System: Retail demand forecasting

## Context and Problem Statement

Forecasts must be reproducible for any past week, including their inputs and training context. The team needs a way to track experiments and production artifacts.

## Decision Drivers

* Past-week reproducibility
* Small team
* Experiment speed

## Considered Options

* End-to-end reproducible lifecycle governance (`v:20.6`)
* Pipeline and experiment version control (`v:20.2`)

## Decision Outcome

Chosen option: "End-to-end reproducible lifecycle governance" (`v:20.6`).

It covers dataset versions, pipeline definitions, dependencies, and training snapshots needed to reproduce a past forecast. “Continuous Intelligence: Moving Machine Learning Application into Production Reliably” and “MLOps Principles” support this traceability approach.

### Consequences

* Retain versioned inputs and training context.
* Record lineage through model promotion.
* Budget effort for metadata and artifact management.

## Pros and Cons of the Options

### End-to-end reproducible lifecycle governance

* Good, because Links data, runs, and models
* Good, because Supports replay and audit
* Bad, because More metadata to maintain
* Sources: `s08_p01`, `s08_p02`, `s22_p03`, `s22_p04`, `s22_p06`, `s22_p08`, `s22_p13`, `s22_p17`

### Pipeline and experiment version control

* Good, because Tracks pipeline changes
* Good, because Supports experiment comparison
* Bad, because Less lifecycle coverage
