# Lifecycle versioning and traceability

* System: Retail demand forecasting

## Context and Problem Statement

Reproducing a forecast for any past week requires identifying the data, code, dependencies, configuration, and model used at that time. New model candidates also need comparable experiment records.

## Decision Drivers

* Past-week reproducibility
* Experiment comparison
* Audit trail

## Considered Options

* End-to-end reproducible lifecycle governance (`v:20.6`)
* Artifact version control (`v:20.1`)

## Decision Outcome

Chosen option: "End-to-end reproducible lifecycle governance" (`v:20.6`).

The brief’s historical replay requirement calls for a complete record, not only a saved model file. “MLOps: What It Is, Why it Matters, and How To Implement It” and Microsoft’s “MLOps: Model management, deployment, and monitoring” describe governance spanning runs, datasets, artifacts, and deployment state. The checked point has no warnings but is unattested.

### Consequences

* Retain immutable input snapshots or equivalent recoverable data versions.
* Record code, dependencies, parameters, and model artifacts for each run.

## Pros and Cons of the Options

### End-to-end reproducible lifecycle governance

* Good, because Versions data and artifacts
* Good, because Links runs to models
* Bad, because Metadata discipline
* Bad, because Storage overhead
* Sources: `s21_p03`, `s21_p05`, `s21_p06`, `s21_p09`, `s21_p10`, `s21_p17`, `s21_p18`, `s25_p01`, `s25_p02`, `s25_p07`

### Artifact version control

* Good, because Tracks model assets
* Good, because Supports reuse
* Bad, because Limited run context
* Bad, because Data lineage gaps
