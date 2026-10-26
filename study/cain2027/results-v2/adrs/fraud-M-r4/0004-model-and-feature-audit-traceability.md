# Model and feature audit traceability

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors must be able to determine which model version and features produced each score. This requires retaining identifiers and linking the score to its serving and feature context.

## Decision Drivers

* Audit traceability

## Considered Options

* Comprehensive ML lifecycle traceability (`v:20.3`)
* Artifact version control (`v:20.1`)
* Pipeline and experiment version control (`v:20.2`)

## Decision Outcome

Chosen option: "Comprehensive ML lifecycle traceability" (`v:20.3`).

Audit traceability decides in favor of linking model artifacts, datasets, runs, metadata, and deployment status. This requires governing more metadata than artifact versioning alone.

### Consequences

* Record the model version and feature identifiers with each score.
* Preserve links from serving records to model and data lineage.

## Pros and Cons of the Options

### Comprehensive ML lifecycle traceability

* Good, because Audit traceability: links lifecycle artifacts and datasets
* Bad, because Audit traceability: more metadata to govern
* Sources: `s08_p01`, `s22_p03`

### Artifact version control

* Good, because Audit traceability: identifies managed artifacts
* Bad, because Audit traceability: limited context for features and runs

### Pipeline and experiment version control

* Good, because Audit traceability: connects pipelines and experiments
* Bad, because Audit traceability: serving context may remain unlinked
