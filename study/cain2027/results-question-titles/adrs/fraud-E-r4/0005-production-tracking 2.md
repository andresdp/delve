# Production tracking

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors need to reconstruct which model and features produced a score. The scoring service also needs operational visibility while handling transaction peaks.

## Decision Drivers

* Auditable predictions
* Production visibility

## Considered Options

* Model in-production tracking (`v:22.4`)
* Monitoring or logging data and predictions (`v:22.2`)
* Model performance monitoring (`v:22.1`)

## Decision Outcome

Chosen option: "Model in-production tracking" (`v:22.4`).

Choose tracking that includes inputs and outputs so score records can be associated with their model and features; apply retention and access controls appropriate to transaction data. (d:22, v:22.4)

### Consequences

* Persist model version and feature references with score records.
* Tracking adds storage and processing load.

## Pros and Cons of the Options

### Model in-production tracking

* Good, because Tracks inputs and outputs
* Good, because Supports interpretability tracking
* Bad, because Storage and processing cost
* Bad, because Sensitive data handling
* Sources: `d:22`, `v:22.4`

### Monitoring or logging data and predictions

* Good, because Captures system data
* Good, because Captures predictions
* Bad, because May omit model context
* Bad, because Log volume
* Sources: `d:22`, `v:22.2`

### Model performance monitoring

* Good, because Tracks model measures
* Bad, because Does not alone identify each score
* Bad, because Needs performance signals
* Sources: `d:22`, `v:22.1`
