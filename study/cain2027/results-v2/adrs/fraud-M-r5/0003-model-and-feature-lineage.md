# Model and feature lineage

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors must be able to determine which model version and features produced a score. Tracking only the model artifact would leave the input data lineage incomplete.

## Decision Drivers

* Audit traceability
* Reproducibility

## Considered Options

* Comprehensive ML lifecycle traceability (`v:20.3`)
* Artifact version control (`v:20.1`)

## Decision Outcome

Chosen option: "Comprehensive ML lifecycle traceability" (`v:20.3`).

Audit traceability decides the choice: it connects model artifacts with training runs and datasets, which artifact-only tracking does not. The trade-off is the added work of capturing and retaining lifecycle metadata.

### Consequences

* Attach model and feature identifiers to each score record.
* Retain lineage metadata for the audit period.

## Pros and Cons of the Options

### Comprehensive ML lifecycle traceability

* Good, because Audit traceability: links runs, datasets, artifacts, and metadata
* Good, because Reproducibility: captures training and pipeline context
* Bad, because Cost: requires integrated metadata governance
* Bad, because Reproducibility: records must be retained and queryable
* Sources: `s08_p01`, `s08_p02`, `s22_p03`, `s22_p04`

### Artifact version control

* Good, because Audit traceability: identifies deployed model artifacts
* Good, because Cost: narrower tracking scope
* Bad, because Audit traceability: does not link each score to its features
* Bad, because Reproducibility: omits dataset and run context
* Sources: `s12_p05`, `s19_p05`
