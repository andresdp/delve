# Track model usage, inputs, outputs, and interpretability in production

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors need to reconstruct which model version and features produced a score. The design space has one production tracking value that includes usage, inputs, outputs, interpretability, and fairness.

## Decision Drivers

* Auditor traceability
* Feature attribution
* Model accountability

## Considered Options

* Model in-production tracking (`v:22.4`)
* Monitoring or logging data and predictions (`v:22.2`)
* No in-production monitoring (`v:22.3`)

## Decision Outcome

Chosen option: "Model in-production tracking" (`v:22.4`).

This is the closest fit for preserving inputs, outputs, and interpretability for later review. The checked point had no warnings, but it was unattested; the design space does not establish that this choice alone captures exact version-to-feature lineage.

### Consequences

* Store a score record linked to model version and feature values.
* Set retention and access rules for audit records.

## Pros and Cons of the Options

### Model in-production tracking

* Good, because Tracks inputs and outputs
* Good, because Includes interpretability
* Bad, because Retention unspecified
* Bad, because Exact version linkage unspecified
* Sources: `d:22`, `v:22.4`

### Monitoring or logging data and predictions

* Good, because Logs system data
* Good, because Logs predictions
* Bad, because Interpretability unspecified
* Bad, because Exact version linkage unspecified
* Sources: `d:22`, `v:22.2`

### No in-production monitoring

* Good, because No monitoring overhead
* Good, because Less stored data
* Bad, because No audit trail
* Bad, because No production visibility
* Sources: `d:22`, `v:22.3`
