# Model performance monitoring

*How should classification quality be monitored?*

* System: Large-scale document classification

## Context and Problem Statement

Operators need to see when classification quality drifts. Monitoring model performance addresses that requirement directly; logging inputs and predictions can supply useful operational context.

## Decision Drivers

* Quality drift visibility
* Operator awareness
* High volume

## Considered Options

* Model performance monitoring (`v:22.1`)
* Monitoring or logging data and predictions (`v:22.2`)
* Model in-production tracking (`v:22.4`)

## Decision Outcome

Chosen option: "Model performance monitoring" (`v:22.1`).

Performance monitoring best matches the explicit need to detect classification quality drift. The rival design point using data and prediction logging has no warning but is unattested as a full combination (`attested_by` is empty), and logging alone does not establish quality.

### Consequences

* Quality measures and evaluation data need definition.
* Operators need thresholds and an alerting workflow.

## Pros and Cons of the Options

### Model performance monitoring

* Good, because Tracks quality measures
* Good, because Surfaces drift
* Bad, because Needs quality signals or labels
* Sources: `d:22`, `v:22.1`

### Monitoring or logging data and predictions

* Good, because Records inputs and outputs
* Good, because Supports investigation
* Bad, because Logs alone do not measure quality
* Sources: `d:22`, `v:22.2`

### Model in-production tracking

* Good, because Tracks usage and outputs
* Good, because Supports broader analysis
* Bad, because Broader tracking effort
* Sources: `d:22`, `v:22.4`
