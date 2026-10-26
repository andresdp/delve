# How should past-week forecasts be reproducible?

* System: Retail demand forecasting

## Context and Problem Statement

The brief requires forecasts to be reproducible for any past week, which calls for retaining enough information to reconstruct the data, pipeline, and model used. The team also needs to compare new model ideas against known runs.

## Decision Drivers

* Past-week reproducibility
* Fast model iteration
* Team of three

## Considered Options

* End-to-end reproducible lifecycle governance (`v:20.6`)
* Pipeline and experiment version control (`v:20.2`)

## Decision Outcome

Chosen option: "End-to-end reproducible lifecycle governance" (`v:20.6`).

Past-week reproducibility decides the choice because preserving dataset versions, run snapshots, dependencies, and model metadata supports reconstruction across the lifecycle. This adds governance work for a small team; the rationale is supported by “MLOps: What It Is, Why it Matters, and How To Implement It (from a Data Scientist Perspective)” and Azure’s model management guidance.

### Consequences

* Retain versioned datasets and run metadata.
* Link deployed models to their training context.
* Budget team time for lifecycle recordkeeping.

## Pros and Cons of the Options

### End-to-end reproducible lifecycle governance

* Good, because Reproducibility: tracks data, runs, artifacts
* Good, because Fast iteration: comparable experiments
* Bad, because Team effort: broad metadata governance
* Sources: `s21_p03`, `s21_p05`, `s21_p06`, `s21_p09`, `s25_p02`, `s25_p07`

### Pipeline and experiment version control

* Good, because Reproducibility: versions pipelines and experiments
* Good, because Team effort: narrower governance scope
* Bad, because Reproducibility: less lifecycle coverage
* Sources: `s04_p01`, `s04_p03`, `s04_p05`, `s17_p03`
