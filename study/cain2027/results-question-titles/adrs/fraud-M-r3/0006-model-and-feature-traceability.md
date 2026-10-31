# Model and feature traceability

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors need to identify the model version and features that produced each score; reproducibility also requires linking deployed artifacts to their training context.

## Decision Drivers

* Model version per score
* Features per score
* Audit traceability

## Considered Options

* Comprehensive ML lifecycle traceability (`v:20.3`)
* Artifact version control (`v:20.1`)
* Data-to-model lineage management (`v:20.4`)

## Decision Outcome

Chosen option: "Comprehensive ML lifecycle traceability" (`v:20.3`).

This option best covers model artifacts, datasets, training context, and deployment metadata. “MLOps Principles” describes lifecycle metadata and model registry practices; per-score audit records must link those identifiers to the features used.

### Consequences

* Persist model version and feature snapshot or references with each score.
* Set retention and access rules for audit records.

## Pros and Cons of the Options

### Comprehensive ML lifecycle traceability

* Good, because Links artifacts and datasets
* Good, because Tracks runs and metadata
* Bad, because Requires lifecycle metadata discipline
* Sources: `s08_p01`, `s22_p03`

### Artifact version control

* Good, because Versions model artifacts
* Bad, because Does not alone link features and score records

### Data-to-model lineage management

* Good, because Connects datasets to models
* Good, because Supports reproducible training
* Bad, because Does not alone record each production score
