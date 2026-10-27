# Track model, feature, and training lineage end to end

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors must be able to identify the exact model version and features behind each score after the transaction.

## Decision Drivers

* Audit traceability
* Model version identification
* Feature provenance

## Considered Options

* Comprehensive ML lifecycle traceability (`v:20.3`)
* Artifact version control (`v:20.1`)

## Decision Outcome

Chosen option: "Comprehensive ML lifecycle traceability" (`v:20.3`).

This choice includes versioned artifacts, training runs, metadata, deployment health, and datasets, providing a stronger basis for answering auditors than artifact versioning alone (Continuous Intelligence: Moving Machine Learning Application into Production Reliably; MLOps Principles). The checked design point had no warnings, though no source attested to the full combination.

### Consequences

* Persist the model version and feature-set identifiers with each score.
* Retain lineage metadata for the audit period.

## Pros and Cons of the Options

### Comprehensive ML lifecycle traceability

* Good, because Links models and datasets
* Good, because Tracks runs and deployment health
* Bad, because Requires lifecycle metadata capture
* Sources: `s08_p01`, `s08_p02`, `s22_p03`, `s22_p06`

### Artifact version control

* Good, because Versions model artifacts
* Bad, because Does not cover full training lineage
* Sources: `s22_p03`
