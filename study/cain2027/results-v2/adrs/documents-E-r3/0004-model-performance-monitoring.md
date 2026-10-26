# Model performance monitoring

*How should classification quality be monitored?*

* System: Large-scale document classification

## Context and Problem Statement

Operators need to see when classification quality drifts, which requires monitoring production behavior and outcomes.

## Decision Drivers

* Quality drift visibility
* Operational response

## Considered Options

* Model performance monitoring (`v:22.1`)
* Monitoring or logging data and predictions (`v:22.2`)
* No in-production monitoring (`v:22.3`)

## Decision Outcome

Chosen option: "Model performance monitoring" (`v:22.1`).

Quality drift visibility decides the choice because the brief explicitly requires operators to detect it. This choice depends on having suitable feedback to measure performance; the design space does not specify how to obtain that feedback.

### Consequences

* Define performance measures and drift thresholds.
* Determine how classification outcomes or labels become available.

## Pros and Cons of the Options

### Model performance monitoring

* Good, because Quality drift visibility: observe model performance parameters
* Bad, because Operational response: measures need suitable feedback data
* Sources: `d:22`, `v:22.1`

### Monitoring or logging data and predictions

* Good, because Operational response: retain inputs and predictions for investigation
* Bad, because Quality drift visibility: logs alone do not establish model quality
* Sources: `d:22`, `v:22.2`

### No in-production monitoring

* Bad, because Quality drift visibility: operators lack production monitoring
* Sources: `d:22`, `v:22.3`
