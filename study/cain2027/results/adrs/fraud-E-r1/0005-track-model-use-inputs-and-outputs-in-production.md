# Track model use, inputs, and outputs in production

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors need to determine which model version and features produced each score after the transaction is authorized.

## Decision Drivers

* Audit traceability
* Model version
* Feature record

## Considered Options

* Model in-production tracking (`v:22.4`)
* Monitoring or logging data and predictions (`v:22.2`)
* No in-production monitoring (`v:22.3`)

## Decision Outcome

Chosen option: "Model in-production tracking" (`v:22.4`).

Tracking model usage, inputs, and outputs most directly supports later audit review (d:22, v:22.4).

### Consequences

* Records must link each score to its model version and feature inputs.
* Retention and access policies remain to be defined.

## Pros and Cons of the Options

### Model in-production tracking

* Good, because Tracks inputs and outputs
* Good, because Tracks model usage
* Bad, because Tracking data must be retained
* Sources: `d:22`, `v:22.4`

### Monitoring or logging data and predictions

* Good, because Logs system data and predictions
* Bad, because Does not specify model usage tracking
* Sources: `d:22`, `v:22.2`

### No in-production monitoring

* Bad, because Weak audit traceability
* Sources: `d:22`, `v:22.3`
