# ML lifecycle traceability

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors need to identify the model version and features behind each score. This requires linking deployed artifacts and datasets to the model lifecycle metadata.

## Decision Drivers

* Auditability: model version
* Auditability: feature traceability

## Considered Options

* Comprehensive ML lifecycle traceability (`v:20.3`)
* Artifact version control (`v:20.1`)
* Data-to-model lineage management (`v:20.4`)

## Decision Outcome

Chosen option: "Comprehensive ML lifecycle traceability" (`v:20.3`).

The requirement to identify both the model version and features decides in favor of lifecycle-wide traceability over artifact-only versioning. We accept broader metadata and governance work; “Continuous Intelligence: Moving Machine Learning Application into Production Reliably” and “MLOps Principles” describe integrated lifecycle tracking.

### Consequences

* Capture model, run, dataset, and deployment metadata.
* Associate score records with the deployed model version and feature snapshot.

## Pros and Cons of the Options

### Comprehensive ML lifecycle traceability

* Good, because Auditability: links artifacts, runs, metadata, and datasets
* Good, because Reproducibility: tracks lifecycle context
* Bad, because Availability: requires lifecycle metadata capture and governance
* Sources: `s08_p01`, `s08_p02`, `s22_p03`, `s22_p04`

### Artifact version control

* Good, because Auditability: identifies managed artifact versions
* Good, because Reproducibility: tracks artifact dependencies
* Bad, because Auditability: does not alone link features and scores
* Sources: `s12_p05`, `s19_p05`

### Data-to-model lineage management

* Good, because Auditability: connects dataset versions to model metadata
* Good, because Reproducibility: preserves training context
* Bad, because Auditability: does not alone establish per-score feature values
* Sources: `s22_p06`, `s22_p08`
