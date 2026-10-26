# Model and training lineage

* System: On-device visual inspection

## Context and Problem Statement

Weekly retraining produces successive model versions from changing labelled-image datasets. The team needs enough history to identify and restore a known version.

## Decision Drivers

* Reproducibility
* Weekly retraining
* Small-team operations

## Considered Options

* End-to-end reproducible lifecycle governance (`v:20.6`)
* Artifact version control (`v:20.1`)

## Decision Outcome

Chosen option: "End-to-end reproducible lifecycle governance" (`v:20.6`).

Reproducibility decides the choice: linking datasets, training runs, and deployed models makes weekly updates traceable, at the cost of added record keeping. “MLOps: What It Is, Why it Matters, and How To Implement It” and “MLOps: Model management, deployment, and monitoring with Azure Machine Learning” describe lifecycle traceability.

### Consequences

* Each release needs associated dataset and training metadata.
* The team takes on more tracking work than artifact versioning alone.

## Pros and Cons of the Options

### End-to-end reproducible lifecycle governance

* Good, because Reproducibility: links data, runs, artifacts, and health
* Bad, because Small-team operations: adds governance work
* Sources: `s21_p05`, `s25_p02`

### Artifact version control

* Good, because Small-team operations: versions deployed artifacts
* Bad, because Reproducibility: limited training and dataset lineage
* Sources: `s19_p05`
