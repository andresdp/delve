# Track production model inputs and outputs

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors need to reconstruct which model version and features produced a score. Production tracking covers model usage, inputs, and outputs in the design space.

## Decision Drivers

* Auditor traceability
* Model version
* Feature provenance

## Considered Options

* Model in-production tracking (`v:22.4`)
* Monitoring or logging data and predictions (`v:22.2`)
* No in-production monitoring (`v:22.3`)

## Decision Outcome

Chosen option: "Model in-production tracking" (`v:22.4`).

Tracking inputs, outputs, and usage best supports later reconstruction of a score. The design point reported no warnings; the batch rival selected basic logging, which does not explicitly cover model version tracking.

### Consequences

* Record model version and scoring inputs with each result.
* Define retention and access controls for audit records.

## Pros and Cons of the Options

### Model in-production tracking

* Good, because Tracks usage, inputs, outputs
* Bad, because Additional tracking data
* Sources: `d:22`, `v:22.4`

### Monitoring or logging data and predictions

* Good, because Logs data and predictions
* Bad, because Version attribution unspecified
* Sources: `d:22`, `v:22.2`

### No in-production monitoring

* Bad, because No production record
* Sources: `d:22`, `v:22.3`
