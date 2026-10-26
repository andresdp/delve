# How should model and feature changes be monitored?

* System: Card-fraud scoring service

## Context and Problem Statement

Fraud patterns and transaction inputs can change after deployment. Auditors also need the system to identify the model version and features associated with a score.

## Decision Drivers

* Audit traceability
* Changing fraud patterns
* Production visibility

## Considered Options

* Comprehensive ML lifecycle traceability (`v:20.3`)
* Artifact version control (`v:20.1`)
* Input and feature-drift monitoring (`v:6.2`)

## Decision Outcome

Chosen option: "Comprehensive ML lifecycle traceability" (`v:20.3`).

Integrated metadata can connect model versions, datasets, and training runs for audit review. “Continuous Intelligence: Moving Machine Learning Application into Production Reliably” and “MLOps Principles” describe lifecycle traceability; drift monitoring is a complementary practice because this dimension combines practices rather than exclusive choices.

### Consequences

* Record model version and feature lineage with each score.
* Retain lifecycle metadata for audit review.

## Pros and Cons of the Options

### Comprehensive ML lifecycle traceability

* Good, because Links runs, data, and models
* Good, because Supports audit trail
* Bad, because Requires lifecycle metadata discipline
* Sources: `s08_p01`, `s22_p03`, `s22_p06`

### Artifact version control

* Good, because Versions deployed artifacts
* Good, because Supports reproducible deployment
* Bad, because Does not alone link scores to feature data
* Sources: `s22_p03`

### Input and feature-drift monitoring

* Good, because Surfaces input changes
* Good, because Helps identify drift
* Bad, because Requires investigation of alerts
* Sources: `s04_p03`, `s06_p02`, `s23_p03`
