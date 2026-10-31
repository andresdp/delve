# Model performance monitoring

*How should production classification quality be monitored?*

* System: Large-scale document classification

## Context and Problem Statement

Operators need to see when classification quality drifts. Monitoring data and predictions can support investigation, while model performance monitoring focuses on model quality.

## Decision Drivers

* Detect quality drift
* Support operator investigation

## Considered Options

* Model performance monitoring (`v:22.1`)
* Monitoring or logging data and predictions (`v:22.2`)
* Model in-production tracking (`v:22.4`)

## Decision Outcome

Chosen option: "Model performance monitoring" (`v:22.1`).

Performance monitoring most directly addresses quality drift. Pair it with data and prediction logging as a complementary practice if investigation requires those records; the design-space alternatives have null exclusivity, so they may be combined. The checked logging point had no warnings and was unattested.

### Consequences

* Define quality measures and alert thresholds.
* Performance monitoring needs a way to obtain quality signals.

## Pros and Cons of the Options

### Model performance monitoring

* Good, because Tracks model performance
* Good, because Targets quality changes
* Bad, because Needs quality measurements
* Sources: `d:22`, `v:22.1`

### Monitoring or logging data and predictions

* Good, because Records inputs and outputs
* Good, because Supports investigation
* Bad, because Logs alone do not measure quality
* Sources: `d:22`, `v:22.2`

### Model in-production tracking

* Good, because Tracks usage and inputs/outputs
* Good, because Can include fairness and interpretability
* Bad, because Broader tracking scope
* Sources: `d:22`, `v:22.4`
