# Production model tracking

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors must later know the model version and features that produced a score. The design space includes tracking model usage, inputs, outputs, interpretability, and fairness (d:22).

## Decision Drivers

* Auditability
* Peak availability

## Considered Options

* Model in-production tracking (`v:22.4`)
* Monitoring or logging data and predictions (`v:22.2`)
* No in-production monitoring (`v:22.3`)

## Decision Outcome

Chosen option: "Model in-production tracking" (`v:22.4`).

Auditability decides: tracking explicitly includes model usage, inputs, and outputs, at the cost of added operational work. The checked combination had no warnings, but no sources attested it.

### Consequences

* Capture model version and feature inputs with each score.
* Tracking storage and access require operational capacity.

## Pros and Cons of the Options

### Model in-production tracking

* Good, because Auditability: tracks usage, inputs, and outputs
* Bad, because Peak availability: tracking adds operational dependencies
* Sources: `d:22`, `v:22.4`

### Monitoring or logging data and predictions

* Good, because Auditability: records system data and predictions
* Bad, because Auditability: feature and model lineage not explicit
* Sources: `d:22`, `v:22.2`

### No in-production monitoring

* Bad, because Auditability: lacks production records
* Sources: `d:22`, `v:22.3`
