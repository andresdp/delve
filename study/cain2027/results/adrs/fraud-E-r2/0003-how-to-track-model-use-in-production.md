# How to track model use in production?

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors need to reconstruct which model version and features produced a score after the transaction.

## Decision Drivers

* Audit trail
* Model version traceability

## Considered Options

* Model in-production tracking (`v:22.4`)
* Monitoring or logging data and predictions (`v:22.2`)
* No in-production monitoring (`v:22.3`)

## Decision Outcome

Chosen option: "Model in-production tracking" (`v:22.4`).

The design space says this option tracks model usage, inputs, and outputs, matching the audit need more directly than general logging or no monitoring (d:22, v:22.4, v:22.2, v:22.3).

### Consequences

* Capture model version and feature inputs with each scored transaction.
* Provide retention and retrieval for audit requests.

## Pros and Cons of the Options

### Model in-production tracking

* Good, because Tracks model usage
* Good, because Tracks inputs and outputs
* Bad, because Requires production tracking
* Sources: `d:22`, `v:22.4`

### Monitoring or logging data and predictions

* Good, because Logs data and predictions
* Bad, because Model usage detail unspecified
* Sources: `d:22`, `v:22.2`

### No in-production monitoring

* Bad, because No production record
* Sources: `d:22`, `v:22.3`
