# How to track model versions and scoring inputs?

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors must be able to reconstruct which model version and features produced a score, so production records must link predictions to their inputs and model identity (d:22).

## Decision Drivers

* Audit traceability
* Reproducibility

## Considered Options

* Model in-production tracking (`v:22.4`)
* Monitoring or logging data and predictions (`v:22.2`)
* No in-production monitoring (`v:22.3`)

## Decision Outcome

Chosen option: "Model in-production tracking" (`v:22.4`).

Audit traceability decides the choice: the design space describes tracking inputs, outputs, and model usage; recording this context costs storage and processing.

### Consequences

* Retain model identity and scoring inputs with each prediction.
* Set retention and access rules for audit records.

## Pros and Cons of the Options

### Model in-production tracking

* Good, because Audit traceability: tracks inputs and outputs
* Bad, because Latency: recording adds work to the request path
* Sources: `d:22`, `v:22.4`

### Monitoring or logging data and predictions

* Good, because Audit traceability: records data and predictions
* Bad, because Reproducibility: may omit model usage details
* Sources: `d:22`, `v:22.2`

### No in-production monitoring

* Bad, because Audit traceability: no production record
* Sources: `d:22`, `v:22.3`
