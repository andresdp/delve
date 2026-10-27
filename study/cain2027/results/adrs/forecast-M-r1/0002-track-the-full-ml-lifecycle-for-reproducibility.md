# Track the full ML lifecycle for reproducibility

* System: Retail demand forecasting

## Context and Problem Statement

Reproducing a past week requires retaining the data and training context behind each forecast. Artifact-only versioning does not cover the complete lifecycle.

## Decision Drivers

* Past-week reproducibility
* Data and model lineage
* Small team

## Considered Options

* End-to-end reproducible lifecycle governance (`v:20.6`)
* Artifact version control (`v:20.1`)

## Decision Outcome

Chosen option: "End-to-end reproducible lifecycle governance" (`v:20.6`).

Choose lifecycle-wide tracking so past forecasts can be tied to dataset versions, pipeline definitions, dependencies, and training runs. “MLOps: What It Is, Why it Matters, and How To Implement It (from a Data Scientist Perspective)” describes these practices together.

### Consequences

* Dataset snapshots and run metadata must be retained.
* Reproducibility depends on capturing pipeline and dependency changes.

## Pros and Cons of the Options

### End-to-end reproducible lifecycle governance

* Good, because Tracks datasets and runs
* Good, because Supports lifecycle audits
* Bad, because More metadata to maintain
* Bad, because Governance overhead
* Sources: `s21_p03`, `s21_p05`, `s21_p06`, `s21_p09`, `s21_p10`, `s25_p01`, `s25_p02`, `s25_p07`

### Artifact version control

* Good, because Versions model assets
* Good, because Supports reuse
* Bad, because Narrower lineage
* Bad, because May omit run context
* Sources: `s12_p05`, `s19_p05`
