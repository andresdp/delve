# Monitor model performance in production

* System: Large-scale document classification

## Context and Problem Statement

Operators need to see when classification quality drifts. The design space includes monitoring specific model performance parameters as well as logging data and predictions.

## Decision Drivers

* Detect quality drift
* Operator visibility

## Considered Options

* Model performance monitoring (`v:22.1`)
* Monitoring or logging data and predictions (`v:22.2`)

## Decision Outcome

Chosen option: "Model performance monitoring" (`v:22.1`).

Direct performance monitoring matches the explicit drift requirement. The checked point has no warnings; the rival logging choice also has no warnings but does not by itself establish that quality is being monitored.

### Consequences

* Define quality measures and alert thresholds.
* Quality labels or other feedback may arrive later.

## Pros and Cons of the Options

### Model performance monitoring

* Good, because Observes model performance
* Good, because Targets quality changes
* Bad, because Needs performance signals
* Sources: `d:22`, `v:22.1`

### Monitoring or logging data and predictions

* Good, because Records inputs and outputs
* Good, because Supports later investigation
* Bad, because Logs alone may miss drift
* Sources: `d:22`, `v:22.2`
