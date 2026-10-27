# Monitor model performance in production

* System: Large-scale document classification

## Context and Problem Statement

Operators need to see when classification quality drifts. The design space distinguishes monitoring model performance from logging data and predictions (d:22).

## Decision Drivers

* Detect quality drift
* Operational visibility

## Considered Options

* Model performance monitoring (`v:22.1`)
* Monitoring or logging data and predictions (`v:22.2`)

## Decision Outcome

Chosen option: "Model performance monitoring" (`v:22.1`).

Performance monitoring most directly addresses the explicit need to see classification quality drift. The batch design point warned against selecting two values for this dimension, so the checked choice uses performance monitoring alone.

### Consequences

* Define quality measures and drift thresholds.
* Determine how labels or review outcomes feed measurement.

## Pros and Cons of the Options

### Model performance monitoring

* Good, because Observes model performance
* Good, because Targets quality changes
* Bad, because Requires performance measures
* Sources: `d:22`, `v:22.1`

### Monitoring or logging data and predictions

* Good, because Records data and outputs
* Good, because Supports operational review
* Bad, because Does not alone establish drift
* Sources: `d:22`, `v:22.2`
