# Model and feature audit trail

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors must later determine which model version and features produced each score. The brief does not specify the retention period or audit format.

## Decision Drivers

* Auditability: model version
* Auditability: features used

## Considered Options

* Comprehensive ML lifecycle traceability (`v:20.3`)
* Artifact version control (`v:20.1`)

## Decision Outcome

Chosen option: "Comprehensive ML lifecycle traceability" (`v:20.3`).

Auditability decides the choice: the comprehensive approach links datasets, training runs, artifacts, and deployment metadata, while artifact version control alone leaves gaps in the requested feature-to-score history. It entails more metadata management. “Continuous Intelligence” and “MLOps Principles” describe lifecycle traceability.

### Consequences

* Record the model and feature context for each scored transaction.
* Retain linked dataset, training, and deployment metadata for later review.

## Pros and Cons of the Options

### Comprehensive ML lifecycle traceability

* Good, because Auditability: links datasets, runs, artifacts, and deployment metadata
* Bad, because Latency: recording metadata adds operational work
* Sources: `s08_p01`, `s08_p02`, `s22_p03`, `s22_p04`, `s22_p06`

### Artifact version control

* Good, because Auditability: identifies managed model artifacts
* Bad, because Auditability: does not alone link feature inputs and training context
* Sources: `s22_p03`
