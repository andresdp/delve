# Track model usage and interpretability in production

* System: Card-fraud scoring service

## Context and Problem Statement

The brief requires auditors to know which model version and features produced each score. Production tracking includes model usage, inputs, outputs, and interpretability in the workspace. (d:22)

## Decision Drivers

* Auditor traceability
* Model and feature attribution

## Considered Options

* Model in-production tracking (`v:22.4`)
* Monitoring or logging data and predictions (`v:22.2`)

## Decision Outcome

Chosen option: "Model in-production tracking" (`v:22.4`).

This alternative most directly covers the required link among model, inputs, and outputs; the feature attribution detail in the brief calls for preserving the features used for each score. The point check returned no warnings, though it was unattested. (d:22, v:22.4)

### Consequences

* Store model version and feature attribution with each score.
* Define retention and access rules for audit records.

## Pros and Cons of the Options

### Model in-production tracking

* Good, because Tracks model usage and inputs
* Good, because Includes interpretability
* Bad, because Requires trace records
* Bad, because Additional storage and operations
* Sources: `d:22`, `v:22.4`

### Monitoring or logging data and predictions

* Good, because Captures data and predictions
* Good, because Supports operational review
* Bad, because Does not explicitly cover interpretability
* Bad, because May omit model usage context
* Sources: `d:22`, `v:22.2`
