# Monitor model performance in production

* System: Large-scale document classification

## Context and Problem Statement

Operators need to see when classification quality drifts. The design space includes model performance monitoring and logging of data and predictions (d:22).

## Decision Drivers

* Detect quality drift
* Operator visibility

## Considered Options

* Model performance monitoring (`v:22.1`)
* Monitoring or logging data and predictions (`v:22.2`)

## Decision Outcome

Chosen option: "Model performance monitoring" (`v:22.1`).

Performance monitoring most directly addresses the stated need to detect classification quality drift. The checked design point had no warnings, but the design space contains no attesting sources.

### Consequences

* Define quality measures and alert thresholds.
* Determine how quality feedback becomes available.

## Pros and Cons of the Options

### Model performance monitoring

* Good, because Tracks performance measures
* Good, because Directly addresses quality
* Bad, because Needs quality measurements
* Sources: `d:22`, `v:22.1`

### Monitoring or logging data and predictions

* Good, because Records inputs and outputs
* Good, because Supports operational review
* Bad, because Logs alone may not reveal drift
* Sources: `d:22`, `v:22.2`
