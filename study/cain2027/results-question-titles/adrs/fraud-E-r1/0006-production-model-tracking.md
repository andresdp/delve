# Production model tracking

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors need to reconstruct which model version and features produced each score. Production tracking can retain model usage, inputs, outputs, and interpretability information.

## Decision Drivers

* Auditor reconstruction
* Model and feature attribution
* Production operation

## Considered Options

* Model in-production tracking (`v:22.4`)
* Monitoring or logging data and predictions (`v:22.2`)
* Model performance monitoring (`v:22.1`)

## Decision Outcome

Chosen option: "Model in-production tracking" (`v:22.4`).

This option includes tracking inputs, outputs, and interpretability, aligning with the request to explain scores later. The implementation should correlate each record with the model version and transaction.

### Consequences

* Persist a traceable record for each score.
* Plan storage and access for audit records.

## Pros and Cons of the Options

### Model in-production tracking

* Good, because Tracks inputs and outputs
* Good, because Tracks usage and interpretability
* Bad, because Adds logging and storage needs
* Bad, because Requires trace correlation
* Sources: `d:22`, `v:22.4`

### Monitoring or logging data and predictions

* Good, because Captures data and predictions
* Good, because Supports operational monitoring
* Bad, because Model attribution needs design
* Bad, because Feature detail may be insufficient
* Sources: `d:22`, `v:22.2`

### Model performance monitoring

* Good, because Tracks model performance
* Good, because Supports quality oversight
* Bad, because Does not alone reconstruct scores
* Bad, because Needs outcome data
* Sources: `d:22`, `v:22.1`
