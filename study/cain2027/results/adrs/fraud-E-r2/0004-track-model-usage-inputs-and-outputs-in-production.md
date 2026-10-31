# Track model usage, inputs, and outputs in production

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors need to know which model version and features produced each score. Production records must connect the transaction, model, and scoring inputs and result.

## Decision Drivers

* Auditor explainability
* Model version traceability
* Feature traceability

## Considered Options

* Model in-production tracking (`v:22.4`)
* Monitoring or logging data and predictions (`v:22.2`)

## Decision Outcome

Chosen option: "Model in-production tracking" (`v:22.4`).

This alternative explicitly includes tracking model usage, inputs, outputs, and interpretability, which best fits the audit requirement. Log the model version and feature values alongside each score.

### Consequences

* Define retention for scoring records.
* Protect logged transaction and feature data.

## Pros and Cons of the Options

### Model in-production tracking

* Good, because Tracks inputs and outputs
* Good, because Includes interpretability
* Bad, because More data to retain
* Bad, because Additional instrumentation
* Sources: `d:22`, `v:22.4`

### Monitoring or logging data and predictions

* Good, because Captures predictions
* Good, because Supports operational review
* Bad, because Model and feature linkage unclear
* Bad, because Audit detail unspecified
* Sources: `d:22`, `v:22.2`
