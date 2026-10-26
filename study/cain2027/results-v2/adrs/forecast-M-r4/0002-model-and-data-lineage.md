# Model and data lineage

* System: Retail demand forecasting

## Context and Problem Statement

Reproducing any past forecast requires knowing which input data, pipeline, experiment, and model produced it. The brief makes this traceability a core requirement.

## Decision Drivers

* Past-week reproducibility
* Fast model comparison

## Considered Options

* End-to-end reproducible lifecycle governance (`v:20.6`)
* Pipeline and experiment version control (`v:20.2`)

## Decision Outcome

Chosen option: "End-to-end reproducible lifecycle governance" (`v:20.6`).

Past-week reproducibility decides the choice because it requires linking datasets, runs, and models across the lifecycle. The trade-off is extra tracking and governance work for a three-person team.

### Consequences

* Retain dataset snapshots or versions and run metadata.
* Keep pipeline, dependency, and model versions associated with each forecast.

## Pros and Cons of the Options

### End-to-end reproducible lifecycle governance

* Good, because Reproducibility: links data, runs, artifacts, and health
* Good, because Fast comparison: tracks experiments
* Bad, because Small-team cost: broad governance to maintain
* Sources: `s21_p03`, `s21_p05`, `s25_p01`

### Pipeline and experiment version control

* Good, because Reproducibility: versions pipelines and artifacts
* Bad, because Traceability: narrower lifecycle coverage
* Sources: `s04_p01`, `s04_p03`
